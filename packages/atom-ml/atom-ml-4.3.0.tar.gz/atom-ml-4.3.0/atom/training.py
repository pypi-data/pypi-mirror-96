# -*- coding: utf-8 -*-

"""Automated Tool for Optimized Modelling (ATOM).

Author: tvdboom
Description: Module containing the training classes.

"""

# Standard packages
import numpy as np
import pandas as pd
from copy import copy
from typeguard import typechecked
from typing import Optional, Union
from sklearn.base import BaseEstimator

# Own modules
from .basetrainer import BaseTrainer
from .plots import BaseModelPlotter, SuccessiveHalvingPlotter, TrainSizingPlotter
from .utils import (
    SEQUENCE_TYPES, TRAIN_TYPES, lst, get_best_score, infer_task,
    composed, method_to_log, crash, CustomDict,
)


class Direct(BaseEstimator, BaseTrainer, BaseModelPlotter):
    """Direct training approach.

    Fit and evaluate over the models. Contrary to SuccessiveHalving
    and TrainSizing, the direct approach only iterates once over the
    models, using the full dataset.

    See basetrainer.py for a description of the parameters.

    """

    def __init__(
        self, models, metric, greater_is_better, needs_proba, needs_threshold,
        n_calls, n_initial_points, est_params, bo_params, bagging, n_jobs,
        verbose, warnings, logger, random_state
    ):
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            n_calls, n_initial_points, est_params, bo_params, bagging,
            n_jobs, verbose, warnings, logger, random_state
        )

    @composed(crash, method_to_log)
    def run(self, *arrays):
        """Run the trainer.

        Parameters
        ----------
        *arrays: sequence of indexables
            Training set and test set. Allowed input formats are:
                - train, test
                - X_train, X_test, y_train, y_test
                - (X_train, y_train), (X_test, y_test)

        """
        self.branch.data, self.branch.idx = self._get_data_and_idx(arrays)
        self.task = infer_task(self.y_train, goal=self.goal)
        self._check_parameters()

        self.log("\nTraining ===================================== >>", 1)
        self.log(f"Models: {', '.join(lst(self.models))}", 1)
        self.log(f"Metric: {', '.join(lst(self.metric))}", 1)

        self._core_iteration()


class SuccessiveHalving(BaseEstimator, BaseTrainer, SuccessiveHalvingPlotter):
    """Successive halving training approach.

    If you want to compare similar models, you can choose to use a
    successive halving approach to run the pipeline. This technique
    is a bandit-based algorithm that fits N models to 1/N of the data.
    The best half are selected to go to the next iteration where the
    process is repeated. This continues until only one model remains,
    which is fitted on the complete dataset. Beware that a model's
    performance can depend greatly on the amount of data on which it
    is trained. For this reason, we recommend only to use this
    technique with similar models, e.g. only using tree-based models.

    See basetrainer.py for a description of the remaining parameters.

    Parameters
    ----------
    skip_runs: int, optional (default=0)
        Skip last `skip_runs` runs of the successive halving.

    """

    def __init__(
        self, models, metric, greater_is_better, needs_proba, needs_threshold,
        skip_runs, n_calls, n_initial_points, est_params, bo_params, bagging,
        n_jobs, verbose, warnings, logger, random_state
    ):
        self.skip_runs = skip_runs
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            n_calls, n_initial_points, est_params, bo_params, bagging,
            n_jobs, verbose, warnings, logger, random_state
        )

    @composed(crash, method_to_log)
    def run(self, *arrays):
        """Run the trainer.

        Parameters
        ----------
        *arrays: sequence of indexables
            Training set and test set. Allowed input formats are:
                - train, test
                - X_train, X_test, y_train, y_test
                - (X_train, y_train), (X_test, y_test)

        """
        self.branch.data, self.branch.idx = self._get_data_and_idx(arrays)
        self.task = infer_task(self.y_train, goal=self.goal)
        self._check_parameters()

        if self.skip_runs < 0:
            raise ValueError(
                "Invalid value for the skip_runs parameter."
                f"Value should be >=0, got {self.skip_runs}."
            )
        elif self.skip_runs >= len(self._models) // 2 + 1:
            raise ValueError(
                "Invalid value for the skip_runs parameter. Less than "
                f"1 run remaining, got n_runs={len(self._models) // 2 + 1} "
                f"and skip_runs={self.skip_runs}."
            )

        self.log("\nTraining ===================================== >>", 1)
        self.log(f"Metric: {', '.join(lst(self.metric))}", 1)

        run = 0
        models = CustomDict()
        og_models = {k: copy(v) for k, v in self._models.items()}
        while len(self._models) > 2 ** self.skip_runs - 1:
            # Create the new set of models for the run
            for m in self._models:
                m.name += str(len(self._models))
                m._pred_attrs = [None] * 10  # Avoid shallow copy
                m._train_idx = len(self.train) // len(self._models)

            # Print stats for this subset of the data
            p = round(100.0 / len(self._models))
            self.log(f"\n\nRun: {run} {'='*32} >>", 1)
            self.log(f"Models: {', '.join(lst(self.models))}", 1)
            self.log(f"Size of training set: {len(self.train)} ({p}%)", 1)
            self.log(f"Size of test set: {len(self.test)}", 1)

            self._core_iteration()
            models.update({m.name: m for m in self._models})

            # Select next models for halving
            best = pd.Series(
                data=[get_best_score(m) for m in self._models],
                index=[m.name for m in self._models],
            ).nlargest(n=len(self._models) // 2, keep="first")
            acronyms = [m.acronym for m in self._models if m.name in best.index]
            self._models = CustomDict(
                {k: copy(v) for k, v in og_models.items() if v.acronym in acronyms}
            )

            run += 1

        self._models = models  # Restore all models


class TrainSizing(BaseEstimator, BaseTrainer, TrainSizingPlotter):
    """Train Sizing training approach.

    When training models, there is usually a trade-off between model
    performance and computation time that is regulated by the number
    of samples in the training set. The TrainSizing class can be used
    to create insights in this trade-off and help determine the optimal
    size of the training set.

    See basetrainer.py for a description of the remaining parameters.

    Parameters
    ----------
    train_sizes: sequence, optional (default=np.linspace(0.2, 1.0, 5))
        Sequence of training set sizes used to run the trainings.
             - If <=1: Fraction of the training set.
             - If >1: Total number of samples.

    """

    def __init__(
        self, models, metric, greater_is_better, needs_proba, needs_threshold,
        train_sizes, n_calls, n_initial_points, est_params, bo_params, bagging,
        n_jobs, verbose, warnings, logger, random_state
    ):
        self.train_sizes = train_sizes
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            n_calls, n_initial_points, est_params, bo_params, bagging,
            n_jobs, verbose, warnings, logger, random_state
        )

    @composed(crash, method_to_log)
    def run(self, *arrays):
        """Run the trainer.

        Parameters
        ----------
        *arrays: sequence of indexables
            Training set and test set. Allowed input formats are:
                - train, test
                - X_train, X_test, y_train, y_test
                - (X_train, y_train), (X_test, y_test)

        """
        self.branch.data, self.branch.idx = self._get_data_and_idx(arrays)
        self.task = infer_task(self.y_train, goal=self.goal)
        self._check_parameters()

        self.log("\nTraining ===================================== >>", 1)
        self.log(f"Models: {', '.join(lst(self.models))}", 1)
        self.log(f"Metric: {', '.join(lst(self.metric))}", 1)

        models = CustomDict()
        og_models = {k: copy(v) for k, v in self._models.items()}
        for run, size in enumerate(self.train_sizes):
            # Select fraction of data to use in this run
            if size <= 1:
                frac = round(size, 2)
                train_idx = int(size * self.branch.idx[0])
            else:
                frac = round(size / self.branch.idx[0], 2)
                train_idx = size

            for m in self._models:
                m.name += str(frac).replace(".", "")  # Add frac to the name
                m._pred_attrs = [None] * 10  # Avoid shallow copy
                m._train_idx = train_idx

            # Print stats for this subset of the data
            p = round(train_idx * 100.0 / self.branch.idx[0])
            self.log(f"\n\nRun: {run} {'='*32} >>", 1)
            self.log(f"Size of training set: {train_idx} ({p}%)", 1)
            self.log(f"Size of test set: {len(self.test)}", 1)

            self._core_iteration()
            models.update({m.name.lower(): m for m in self._models})

            # Create next models for sizing
            self._models = CustomDict({k: copy(v) for k, v in og_models.items()})

        self._models = models  # Restore original models


class DirectClassifier(Direct):
    """Direct trainer for classification tasks."""

    @typechecked
    def __init__(
        self,
        models: Union[str, callable, SEQUENCE_TYPES],
        metric: Optional[Union[str, callable, SEQUENCE_TYPES]] = None,
        greater_is_better: Union[bool, SEQUENCE_TYPES] = True,
        needs_proba: Union[bool, SEQUENCE_TYPES] = False,
        needs_threshold: Union[bool, SEQUENCE_TYPES] = False,
        n_calls: Union[int, SEQUENCE_TYPES] = 0,
        n_initial_points: Union[int, SEQUENCE_TYPES] = 5,
        est_params: Optional[dict] = None,
        bo_params: Optional[dict] = None,
        bagging: Union[int, SEQUENCE_TYPES] = 0,
        n_jobs: int = 1,
        verbose: int = 0,
        warnings: Union[bool, str] = True,
        logger: Optional[Union[str, callable]] = None,
        random_state: Optional[int] = None,
    ):
        self.goal = "classification"
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            n_calls, n_initial_points, est_params, bo_params, bagging,
            n_jobs, verbose, warnings, logger, random_state
        )


class DirectRegressor(Direct):
    """Direct trainer for regression tasks."""

    @typechecked
    def __init__(
        self,
        models: Union[str, callable, SEQUENCE_TYPES],
        metric: Optional[Union[str, callable, SEQUENCE_TYPES]] = None,
        greater_is_better: Union[bool, SEQUENCE_TYPES] = True,
        needs_proba: Union[bool, SEQUENCE_TYPES] = False,
        needs_threshold: Union[bool, SEQUENCE_TYPES] = False,
        n_calls: Union[int, SEQUENCE_TYPES] = 0,
        n_initial_points: Union[int, SEQUENCE_TYPES] = 5,
        est_params: Optional[dict] = None,
        bo_params: Optional[dict] = None,
        bagging: Union[int, SEQUENCE_TYPES] = 0,
        n_jobs: int = 1,
        verbose: int = 0,
        warnings: Union[bool, str] = True,
        logger: Optional[Union[str, callable]] = None,
        random_state: Optional[int] = None,
    ):
        self.goal = "regression"
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            n_calls, n_initial_points, est_params, bo_params, bagging,
            n_jobs, verbose, warnings, logger, random_state
        )


class SuccessiveHalvingClassifier(SuccessiveHalving):
    """SuccessiveHalving trainer for classification tasks."""

    @typechecked
    def __init__(
        self,
        models: Union[str, callable, SEQUENCE_TYPES],
        metric: Optional[Union[str, callable, SEQUENCE_TYPES]] = None,
        greater_is_better: Union[bool, SEQUENCE_TYPES] = True,
        needs_proba: Union[bool, SEQUENCE_TYPES] = False,
        needs_threshold: Union[bool, SEQUENCE_TYPES] = False,
        skip_runs: int = 0,
        n_calls: Union[int, SEQUENCE_TYPES] = 0,
        n_initial_points: Union[int, SEQUENCE_TYPES] = 5,
        est_params: Optional[dict] = None,
        bo_params: Optional[dict] = None,
        bagging: Union[int, SEQUENCE_TYPES] = 0,
        n_jobs: int = 1,
        verbose: int = 0,
        warnings: Union[bool, str] = True,
        logger: Optional[Union[str, callable]] = None,
        random_state: Optional[int] = None,
    ):
        self.goal = "classification"
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            skip_runs, n_calls, n_initial_points, est_params, bo_params,
            bagging, n_jobs, verbose, warnings, logger, random_state
        )


class SuccessiveHalvingRegressor(SuccessiveHalving):
    """SuccessiveHalving trainer for regression tasks."""

    @typechecked
    def __init__(
        self,
        models: Union[str, callable, SEQUENCE_TYPES],
        metric: Optional[Union[str, callable, SEQUENCE_TYPES]] = None,
        greater_is_better: Union[bool, SEQUENCE_TYPES] = True,
        needs_proba: Union[bool, SEQUENCE_TYPES] = False,
        needs_threshold: Union[bool, SEQUENCE_TYPES] = False,
        skip_runs: int = 0,
        n_calls: Union[int, SEQUENCE_TYPES] = 0,
        n_initial_points: Union[int, SEQUENCE_TYPES] = 5,
        est_params: Optional[dict] = None,
        bo_params: Optional[dict] = None,
        bagging: Union[int, SEQUENCE_TYPES] = 0,
        n_jobs: int = 1,
        verbose: int = 0,
        warnings: Union[bool, str] = True,
        logger: Optional[Union[str, callable]] = None,
        random_state: Optional[int] = None,
    ):
        self.goal = "regression"
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            skip_runs, n_calls, n_initial_points, est_params, bo_params,
            bagging, n_jobs, verbose, warnings, logger, random_state
        )


class TrainSizingClassifier(TrainSizing):
    """TrainSizing trainer for classification tasks."""

    @typechecked
    def __init__(
        self,
        models: Union[str, callable, SEQUENCE_TYPES],
        metric: Optional[Union[str, callable, SEQUENCE_TYPES]] = None,
        greater_is_better: Union[bool, SEQUENCE_TYPES] = True,
        needs_proba: Union[bool, SEQUENCE_TYPES] = False,
        needs_threshold: Union[bool, SEQUENCE_TYPES] = False,
        train_sizes: TRAIN_TYPES = np.linspace(0.2, 1.0, 5),
        n_calls: Union[int, SEQUENCE_TYPES] = 0,
        n_initial_points: Union[int, SEQUENCE_TYPES] = 5,
        est_params: Optional[dict] = None,
        bo_params: Optional[dict] = None,
        bagging: Union[int, SEQUENCE_TYPES] = 0,
        n_jobs: int = 1,
        verbose: int = 0,
        warnings: Union[bool, str] = True,
        logger: Optional[Union[str, callable]] = None,
        random_state: Optional[int] = None,
    ):
        self.goal = "classification"
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            train_sizes, n_calls, n_initial_points, est_params, bo_params,
            bagging, n_jobs, verbose, warnings, logger, random_state
        )


class TrainSizingRegressor(TrainSizing):
    """TrainSizing trainer for regression tasks."""

    @typechecked
    def __init__(
        self,
        models: Union[str, callable, SEQUENCE_TYPES],
        metric: Optional[Union[str, callable, SEQUENCE_TYPES]] = None,
        greater_is_better: Union[bool, SEQUENCE_TYPES] = True,
        needs_proba: Union[bool, SEQUENCE_TYPES] = False,
        needs_threshold: Union[bool, SEQUENCE_TYPES] = False,
        train_sizes: TRAIN_TYPES = np.linspace(0.2, 1.0, 5),
        n_calls: Union[int, SEQUENCE_TYPES] = 0,
        n_initial_points: Union[int, SEQUENCE_TYPES] = 5,
        est_params: Optional[dict] = None,
        bo_params: Optional[dict] = None,
        bagging: Union[int, SEQUENCE_TYPES] = 0,
        n_jobs: int = 1,
        verbose: int = 0,
        warnings: Union[bool, str] = True,
        logger: Optional[Union[str, callable]] = None,
        random_state: Optional[int] = None,
    ):
        self.goal = "regression"
        super().__init__(
            models, metric, greater_is_better, needs_proba, needs_threshold,
            train_sizes, n_calls, n_initial_points, est_params, bo_params,
            bagging, n_jobs, verbose, warnings, logger, random_state
        )
