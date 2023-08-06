# -*- coding: utf-8 -*-

"""Automated Tool for Optimized Modelling (ATOM).

Author: tvdboom
Description: Module containing the ModelOptimizer class.

"""

# Standard packages
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Optional
from inspect import signature
from datetime import datetime
from joblib import Parallel, delayed
from typeguard import typechecked

# Sklearn
from sklearn.base import clone
from sklearn.utils import resample
from sklearn.model_selection import StratifiedShuffleSplit, ShuffleSplit
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV

# Others
from skopt.utils import use_named_args
from skopt.optimizer import base_minimize, gp_minimize, forest_minimize, gbrt_minimize

# Own modules
from .data_cleaning import Scaler
from .basemodel import BaseModel
from .plots import SuccessiveHalvingPlotter, TrainSizingPlotter
from .utils import (
    flt, lst, arr, time_to_str, composed, get_best_score, crash, method_to_log,
)


class ModelOptimizer(BaseModel, SuccessiveHalvingPlotter, TrainSizingPlotter):
    """Class for model optimization.

    Contains the Bayesian Optimization, fitting and bagging of the
    models as well as some utility attributes not shared with the
    ensemble classes.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Skip if called from FeatureSelector
        if hasattr(self.T, "_branches"):
            self.branch = self.T._branches[self.T._current]
            self._train_idx = self.branch.idx[0]  # Can change for sh and ts
            if self.needs_scaling and not self.T.scaled:
                self.scaler = Scaler().fit(self.X_train)

        # BO attributes
        self._iter = 0
        self._init_bo = None
        self._pbar = None
        self._stopped = None
        self.bo = pd.DataFrame(
            columns=["params", "model", "score", "time_iteration", "time"],
            index=pd.Index([], name="call"),
        )

        # Parameter attributes
        self._n_calls = 0
        self._n_initial_points = 5
        self._bagging = 0
        self._dimensions = []
        self._est_params = {}
        self._est_params_fit = {}

        # ModelOptimizer attributes
        self.best_params = None
        self.metric_bo = None
        self.time_bo = None
        self.metric_train = None
        self.metric_test = None
        self.time_fit = None
        self.metric_bagging = None
        self.mean_bagging = None
        self.std_bagging = None
        self.time_bagging = None
        self.time = None

    def __repr__(self):
        out_1 = f"{self.fullname}\n --> Estimator: {self.estimator.__class__.__name__}"
        out_2 = [
            f"{m.name}: {round(get_best_score(self, i), 4)}"
            for i, m in enumerate(self.T._metric)
        ]
        return out_1 + f"\n --> Evaluation: {'   '.join(out_2)}"

    def _check_est_params(self):
        """Make sure the parameters are valid keyword argument for the estimator."""
        signature_init = signature(self.get_estimator().__init__).parameters
        signature_fit = signature(self.get_estimator().fit).parameters

        # The parameter is always accepted if the estimator accepts kwargs
        for param in self._est_params:
            if param not in signature_init and "kwargs" not in signature_init:
                raise ValueError(
                    f"Invalid value for the est_params parameter. "
                    f"Got unknown parameter {param} for estimator "
                    f"{self.get_estimator().__class__.__name__}."
                )

        for param in self._est_params_fit:
            if param not in signature_fit and "kwargs" not in signature_fit:
                raise ValueError(
                    f"Invalid value for the est_params parameter. Got "
                    f"unknown parameter {param} for the fit method of "
                    f"estimator {self.get_estimator().__class__.__name__}."
                )

    def get_params(self, x):
        """Get a dictionary of the model's hyperparameters.

        For numerical parameters, the second arg in value indicates
        if the number should have decimals and how many.

        Parameters
        ----------
        x: list
            Hyperparameters returned by the BO in order of self.params.

        """
        params = {}
        for i, (key, value) in enumerate(self.params.items()):
            params[key] = round(x[i], value[1]) if value[1] else x[i]

        return params

    def get_init_values(self):
        """Return the default values of the model's hyperparameters."""
        return [value[0] for value in self.params.values()]

    def bayesian_optimization(self):
        """Run the bayesian optimization algorithm.

        Search for the best combination of hyperparameters. The
        function to optimize is evaluated either with a K-fold
        cross-validation on the training set or using a different
        split for train and validation set every iteration.

        """
        def optimize(**params):
            """Optimization function for the BO.

            Parameters
            ----------
            params: dict
               Model's hyperparameters used in this call of the BO.

            Returns
            -------
            score: float
                Score achieved by the model.

            """
            def fit_model(train_idx, val_idx):
                """Fit the model. Function for parallelization.

                Divide the training set in a (sub)train and validation
                set for this fit. Fit the model on custom_fit if exists,
                else normally. Return the score on the validation set.

                Parameters
                ----------
                train_idx: list
                    Indices for the subtrain set.

                val_idx: list
                    Indices for the validation set.

                Returns
                -------
                score: float
                    Score of the fitted model on the validation set.

                """
                X_subtrain = self.X_train.loc[train_idx]
                y_subtrain = self.y_train.loc[train_idx]
                X_val = self.X_train.loc[val_idx]
                y_val = self.y_train.loc[val_idx]

                # Match the sample_weights with the length of the subtrain set
                # Make copy of est_params to not alter the mutable variable
                est_copy = self._est_params_fit.copy()
                if "sample_weight" in est_copy:
                    est_copy["sample_weight"] = [
                        self._est_params_fit["sample_weight"][i] for i in train_idx
                    ]

                if hasattr(self, "custom_fit"):
                    self.custom_fit(
                        est=est,
                        train=(X_subtrain, y_subtrain),
                        validation=(X_val, y_val),
                        params=est_copy
                    )

                    # Alert if early stopping was applied (only for cv=1)
                    if self.T._cv == 1 and self._stopped:
                        self.T.log(
                            f"Early stop at iteration {self._stopped[0]} "
                            f"of {self._stopped[1]}.", 2
                        )
                else:
                    est.fit(arr(X_subtrain), y_subtrain, **est_copy)

                # Calculate metrics on the validation set
                return [metric(est, arr(X_val), y_val) for metric in self.T._metric]

            t_iter = datetime.now()  # Get current time for start of the iteration

            # Print iteration and time
            self._iter += 1
            if self._iter > self._n_initial_points:
                call = f"Iteration {self._iter}"
            else:
                call = f"Initial point {self._iter}"

            if self._pbar:
                self._pbar.set_description(call)
            len_ = "-" * (48 - len(call))
            self.T.log(f"{call} {len_}", 2)
            self.T.log(f"Parameters --> {params}", 2)

            est = self.get_estimator({**self._est_params, **params})

            # Same splits per model, but different for every iteration of the BO
            rs = self.T.random_state + self._iter if self.T.random_state else None

            if self.T._cv == 1:
                # Select test_size from ATOM or use default of 0.2
                t_size = self.T._test_size if hasattr(self.T, "_test_size") else 0.2
                kwargs = dict(test_size=t_size, random_state=rs)
                if self.T.goal.startswith("class"):
                    # Folds are made preserving the % of samples for each class
                    split = StratifiedShuffleSplit(1, **kwargs)
                else:
                    split = ShuffleSplit(1, **kwargs)

                scores = fit_model(*next(split.split(self.X_train, self.y_train)))

            else:  # Use cross validation to get the score
                kwargs = dict(n_splits=self.T._cv, shuffle=True, random_state=rs)
                if self.T.goal.startswith("class"):
                    # Folds are made preserving the % of samples for each class
                    k_fold = StratifiedKFold(**kwargs)
                else:
                    k_fold = KFold(**kwargs)

                # Parallel loop over fit_model
                jobs = Parallel(self.T.n_jobs)(
                    delayed(fit_model)(i, j)
                    for i, j in k_fold.split(self.X_train, self.y_train)
                )
                scores = list(np.mean(jobs, axis=0))

            # Append row to the bo attribute
            t = time_to_str(t_iter)
            t_tot = time_to_str(self._init_bo)
            self.bo.loc[call] = {
                "params": params,
                "estimator": est,
                "score": flt(scores),
                "time_iteration": t,
                "time": t_tot,
            }

            # Update the progress bar
            if self._pbar:
                self._pbar.update(1)

            # Print output of the BO
            out = [
                f"{m.name}: {scores[i]:.4f}  Best {m.name}: "
                f"{max([lst(s)[i] for s in self.bo.score]):.4f}"
                for i, m in enumerate(self.T._metric)
            ]
            self.T.log(f"Evaluation --> {'   '.join(out)}", 2)
            self.T.log(f"Time iteration: {t}   Total time: {t_tot}", 2)

            return -scores[0]  # Negative since skopt tries to minimize

        # Running optimization ===================================== >>

        if self._n_calls < self._n_initial_points:
            raise ValueError(
                "Invalid value for the n_calls parameter. Value "
                f"should be >n_initial_points, got {self._n_calls}."
            )

        self.T.log(f"\n\nRunning BO for {self.fullname}...", 1)

        self._init_bo = datetime.now()
        if self.T.verbose == 1:
            self._pbar = tqdm(total=self._n_calls, desc="Random start 1")

        self._check_est_params()  # Check validity of parameters

        # Drop dimensions from BO if already in est_params
        for param in self._est_params:
            if param in self.params:
                self.params.pop(param)

        # Specify model dimensions
        def pre_defined_hyperparameters(x):
            return optimize(**self.get_params(x))

        # Get custom dimensions (if provided)
        if self._dimensions:
            @use_named_args(self._dimensions)
            def custom_hyperparameters(**x):
                return optimize(**x)

            dimensions = self._dimensions
            func = custom_hyperparameters  # Use custom hyperparameters

        else:  # If there were no custom dimensions, use the default
            dimensions = self.get_dimensions()
            func = pre_defined_hyperparameters  # Default optimization func

        # If only 1 initial point, use the model's default parameters
        x0 = None
        if self._n_initial_points == 1 and hasattr(self, "get_init_values"):
            x0 = self.get_init_values()

        # Prepare keyword arguments for the optimizer
        kwargs = dict(
            func=func,
            dimensions=dimensions,
            n_calls=self._n_calls,
            n_initial_points=self._n_initial_points,
            x0=x0,
            callback=self.T._callbacks,
            n_jobs=self.T.n_jobs,
            random_state=self.T.random_state,
            **self.T._bo_kwargs,
        )

        if str(self.T._base_estimator).lower() == "gp":
            optimizer = gp_minimize(**kwargs)
        elif str(self.T._base_estimator).lower() == "et":
            optimizer = forest_minimize(base_estimator="ET", **kwargs)
        elif str(self.T._base_estimator).lower() == "rf":
            optimizer = forest_minimize(base_estimator="RF", **kwargs)
        elif str(self.T._base_estimator).lower() == "gbrt":
            optimizer = gbrt_minimize(**kwargs)
        else:
            optimizer = base_minimize(base_estimator=self.T._base_estimator, **kwargs)

        if self._pbar:
            self._pbar.close()

        # Optimal parameters found by the BO
        # Return from skopt wrapper to get dict of custom hyperparameter space
        if func is pre_defined_hyperparameters:
            self.best_params = self.get_params(optimizer.x)
        else:
            @use_named_args(dimensions)
            def get_custom_params(**x):
                return x

            self.best_params = get_custom_params(optimizer.x)

        # Optimal score found by the BO
        self.metric_bo = self.bo.score.max(axis=0)

        # Save best model (not yet fitted)
        self.estimator = self.get_estimator({**self._est_params, **self.best_params})

        # Get the BO duration
        self.time_bo = time_to_str(self._init_bo)

        # Print results
        self.T.log(f"\nResults for {self.fullname}:{' ':9s}", 1)
        self.T.log("Bayesian Optimization ---------------------------", 1)
        self.T.log(f"Best parameters --> {self.best_params}", 1)
        out = [
            f"{m.name}: {round(lst(self.metric_bo)[i], 4)}"
            for i, m in enumerate(self.T._metric)
        ]
        self.T.log(f"Best evaluation --> {'   '.join(out)}", 1)
        self.T.log(f"Time elapsed: {self.time_bo}", 1)

    def fit(self):
        """Fit and validate the model."""
        t_init = datetime.now()

        # In case the bayesian_optimization method wasn't called
        if self.estimator is None:
            self._check_est_params()
            self.estimator = self.get_estimator(self._est_params)

        # Fit the selected model on the complete training set
        if hasattr(self, "custom_fit"):
            self.custom_fit(
                est=self.estimator,
                train=(self.X_train, self.y_train),
                validation=(self.X_test, self.y_test),
                params=self._est_params_fit
            )
        else:
            self.estimator.fit(arr(self.X_train), self.y_train, **self._est_params_fit)

        # Save metric scores on complete training and test set
        self.metric_train = flt([
            metric(self.estimator, arr(self.X_train), self.y_train)
            for metric in self.T._metric
        ])
        self.metric_test = flt([
            metric(self.estimator, arr(self.X_test), self.y_test)
            for metric in self.T._metric
        ])

        # Print stats ============================================== >>

        if self.bo.empty:
            self.T.log(f"\n\nResults for {self.fullname}:{' ':9s}", 1)
        self.T.log("Fit ---------------------------------------------", 1)
        if self._stopped:
            self.T.log(
                f"Early stop at iteration {self._stopped[0]} of {self._stopped[1]}.", 1
            )
        out_train = [
            f"{m.name}: {round(lst(self.metric_train)[i], 4)}"
            for i, m in enumerate(self.T._metric)
        ]
        self.T.log(f"Train evaluation --> {'   '.join(out_train)}", 1)
        out_test = [
            f"{m.name}: {round(lst(self.metric_test)[i], 4)}"
            for i, m in enumerate(self.T._metric)
        ]
        self.T.log(f"Test evaluation --> {'   '.join(out_test)}", 1)

        # Get duration and print to log
        self.time_fit = time_to_str(t_init)
        self.T.log(f"Time elapsed: {self.time_fit}", 1)

    def bootstrap_aggregating(self):
        """Apply a bootstrap aggregating (bagging) algorithm.

        Take bootstrap samples from the training set and test them on
        the test set to get a distribution of the model's results.

        """
        t_init = datetime.now()

        self.metric_bagging = []
        for _ in range(self._bagging):
            # Create samples with replacement
            sample_x, sample_y = resample(self.X_train, self.y_train)

            # Clone to not overwrite when fitting
            estimator = clone(self.estimator)

            # Fit on bootstrapped set and predict on the independent test set
            if hasattr(self, "custom_fit"):
                self.custom_fit(
                    est=estimator,
                    train=(sample_x, sample_y),
                    validation=None,
                    params=self._est_params_fit
                )
            else:
                estimator.fit(arr(sample_x), sample_y, **self._est_params_fit)

            self.metric_bagging.append(
                flt([
                    metric(estimator, arr(self.X_test), self.y_test)
                    for metric in self.T._metric
                ])
            )

        # Separate for multi-metric, transform numpy types to python types
        if len(self.T._metric) == 1:
            self.mean_bagging = np.mean(self.metric_bagging, axis=0).item()
            self.std_bagging = np.std(self.metric_bagging, axis=0).item()
        else:
            self.metric_bagging = list(zip(*self.metric_bagging))
            self.mean_bagging = np.mean(self.metric_bagging, axis=1).tolist()
            self.std_bagging = np.std(self.metric_bagging, axis=1).tolist()

        self.T.log("Bagging -----------------------------------------", 1)
        out = [
            f"{m.name}: {round(lst(self.mean_bagging)[i], 4)}"
            f" \u00B1 {round(lst(self.std_bagging)[i], 4)}"
            for i, m in enumerate(self.T._metric)
        ]
        self.T.log(f"Evaluation --> {'   '.join(out)}", 1)

        self.time_bagging = time_to_str(t_init)
        self.T.log(f"Time elapsed: {self.time_bagging}", 1)

    # Utility methods ============================================== >>

    def _final_output(self):
        """Returns the model's final output as a string."""
        # If bagging was used, we use a different format
        if self.mean_bagging is None:
            out = "   ".join([
                f"{m.name}: {round(lst(self.metric_test)[i], 4)}"
                for i, m in enumerate(self.T._metric)
            ])
        else:
            out = "   ".join([
                f"{m.name}: {round(lst(self.mean_bagging)[i], 4)} "
                f"\u00B1 {round(lst(self.std_bagging)[i], 4)}"
                for i, m in enumerate(self.T._metric)
            ])

        # Annotate if model overfitted when train 20% > test
        metric_train = lst(self.metric_train)
        metric_test = lst(self.metric_test)
        if metric_train[0] - 0.2 * metric_train[0] > metric_test[0]:
            out += " ~"

        return out

    @composed(crash, method_to_log)
    def calibrate(self, **kwargs):
        """Calibrate the model.

        Applies probability calibration on the winning model. The
        calibration is done with the CalibratedClassifierCV class from
        sklearn. The estimator will be trained via cross-validation on
        a subset of the training data, using the rest to fit the
        calibrator. The new classifier will replace the `estimator`
        attribute. All prediction attributes will reset.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments for the CalibratedClassifierCV
            instance. Using cv="prefit" will use the trained model and
            fit the calibrator on the test set. Note that doing this
            will result in data leakage in the test set. Use this only
            if you have another, independent set for testing.

        """
        if self.T.goal.startswith("reg"):
            raise PermissionError(
                "The calibrate method is only available for classification tasks!"
            )

        calibrator = CalibratedClassifierCV(self.estimator, **kwargs)
        if kwargs.get("cv") != "prefit":
            self.estimator = calibrator.fit(self.X_train, self.y_train)
        else:
            self.estimator = calibrator.fit(self.X_test, self.y_test)

        self.T.log(f"Model {self.name} successfully calibrated!")

        # Reset all prediction attrs since the model's estimator changed
        self._pred_attrs = [None] * 10

    @composed(crash, method_to_log, typechecked)
    def rename(self, name: Optional[str] = None):
        """Change the model's tag.

        Note that the acronym always stays at the beginning of the
        model's name.

        Parameters
        ----------
        name: str or None, optional (default=None)
            New tag for the model. If None, the tag is removed.

        """
        name = name.lower()

        # Drop the acronym if not provided by the user
        if name.startswith(self.acronym.lower()):
            name = name[len(self.acronym):]

        # Add the acronym (with right capitalization)
        name = self.acronym + name

        # Replace the model in the _models attribute
        self.T._models.insert(self.name, name, self)
        self.T._models.pop(self.name)
        self.T.log(f"Model {self.name} successfully renamed to {name}!")
        self.name = name

    @composed(crash, method_to_log, typechecked)
    def save_estimator(self, filename: Optional[str] = None):
        """Save the estimator to a pickle file.

        Parameters
        ----------
        filename: str, optional (default=None)
            Name of the file. If None or "auto", the estimator's
            __name__ is used.

        """
        if not filename:
            filename = self.estimator.__class__.__name__
        elif filename == "auto" or filename.endswith("/auto"):
            filename = filename.replace("auto", self.estimator.__class__.__name__)

        pickle.dump(self.estimator, open(filename, "wb"))
        self.T.log(f"{self.fullname} estimator saved successfully!", 1)
