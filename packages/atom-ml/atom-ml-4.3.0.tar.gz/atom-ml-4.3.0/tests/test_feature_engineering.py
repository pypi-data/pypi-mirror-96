# coding: utf-8

"""
Automated Tool for Optimized Modelling (ATOM)
Author: tvdboom
Description: Unit tests for feature_engineering.py

"""

# Standard packages
import pytest
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import f_regression

# Own modules
from atom.feature_engineering import FeatureGenerator, FeatureSelector
from .utils import X_bin, y_bin, X_class, y_class, X_reg, y_reg


# Test FeatureGenerator ============================================ >>

def test_n_features_parameter_negative():
    """Assert that an error is raised when n_features is negative."""
    fg = FeatureGenerator(n_features=-2)
    with pytest.raises(ValueError, match=r".*should be >0.*"):
        fg.fit(X_bin, y_bin)


def test_population_parameter():
    """Assert that an error is raised when population is invalid."""
    fg = FeatureGenerator(strategy="GFG", population=30)
    pytest.raises(ValueError, fg.fit, X_reg, y_reg)


def test_generations_parameter():
    """Assert that an error is raised when generations is invalid."""
    fg = FeatureGenerator(strategy="GFG", generations=0)
    pytest.raises(ValueError, fg.fit, X_bin, y_bin)


def test_n_features_parameter_not_one_percent():
    """Assert that the n_features parameter is within 1% of population."""
    fg = FeatureGenerator(strategy="GFG", n_features=23, population=200)
    with pytest.raises(ValueError, match=r".*should be <1%.*"):
        fg.fit(X_bin, y_bin)


def test_strategy_parameter():
    """Assert that the strategy parameter is either "DFS", "GFG" or "genetic"."""
    fg = FeatureGenerator(strategy="invalid")
    with pytest.raises(ValueError, match=r".*should be either 'dfs'.*"):
        fg.fit(X_bin, y_bin)


def test_operators_parameter():
    """Assert that all operators are valid."""
    fg = FeatureGenerator("GFG", n_features=None, operators=("div", "invalid"))
    with pytest.raises(ValueError, match=r".*value in the operators.*"):
        fg.fit(X_bin, y_bin)


def test_n_features_above_maximum():
    """Assert that n_features becomes maximum if more than maximum for "DFS"."""
    generator = FeatureGenerator(n_features=1000, operators="log", random_state=1)
    _ = generator.fit_transform(X_bin, y_bin)
    assert generator.n_features == 30


def test_genetic_non_improving_features():
    """Assert that the code doesn't fail if there are no new improving features."""
    generator = FeatureGenerator(
        strategy="gfg", generations=5, population=300, operators="sqrt", random_state=1
    )
    _ = generator.fit_transform(X_reg, y_reg)
    assert generator.genetic_features is None


def test_attribute_genetic_features():
    """Assert that the genetic_features attribute is created."""
    generator = FeatureGenerator(
        strategy="gfg", generations=3, population=200, random_state=1
    )
    _ = generator.fit_transform(X_bin, y_bin)
    assert not generator.genetic_features.empty


def test_genetic_maximum_features():
    """Assert that the features are 1% of the population for n_features=None."""
    generator = FeatureGenerator(
        strategy="gfg", n_features=None, generations=4, population=400, random_state=1
    )
    X = generator.fit_transform(X_bin, y_bin)
    assert X.shape[1] == X_bin.shape[1] + 4


def test_updated_dataset():
    """Assert that the feature set contains the new features."""
    generator = FeatureGenerator(
        strategy="gfg", n_features=1, generations=4, population=1000, random_state=1
    )
    X = generator.fit_transform(X_bin, y_bin)
    assert X.shape[1] == X_bin.shape[1] + 1

    generator = FeatureGenerator(strategy="dfs", n_features=None, random_state=1)
    X = generator.fit_transform(X_bin, y_bin)
    assert X.shape[1] > X_bin.shape[1]


# Test FeatureSelector ============================================= >>

def test_unknown_strategy_parameter():
    """Assert that an error is raised when strategy is unknown."""
    fs = FeatureSelector(strategy="invalid")
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_solver_parameter_empty_univariate():
    """Assert that an error is raised when solver is None for univariate."""
    fs = FeatureSelector(strategy="univariate")
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_raise_unknown_solver_univariate():
    """Assert that an error is raised when the solver is unknown."""
    fs = FeatureSelector(strategy="univariate", solver="invalid")
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_solver_auto_PCA():
    """Assert that the solver is set to "auto" when None."""
    fs = FeatureSelector(strategy="PCA", solver=None)
    fs.fit(X_bin, y_bin)
    assert fs.solver == "auto"


def test_solver_parameter_empty_SFM():
    """Assert that an error is raised when solver is None for SFM strategy."""
    fs = FeatureSelector(strategy="SFM", solver=None)
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_goal_attribute():
    """Assert that the goal is deduced from the model's name."""
    # For classification tasks
    fs = FeatureSelector(strategy="SFM", solver="LGB_class")
    fs.fit(X_bin, y_bin)
    assert fs.goal == "classification"

    # For regression tasks
    fs = FeatureSelector(strategy="SFM", solver="LGB_reg")
    fs.fit(X_reg, y_reg)
    assert fs.goal == "regression"


def test_solver_parameter_invalid_value():
    """Assert that an error is raised when solver is unknown."""
    fs = FeatureSelector(strategy="RFE", solver="invalid")
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_n_features_parameter():
    """Assert that an error is raised when n_features is invalid."""
    fs = FeatureSelector(strategy="SFM", solver="XGB_reg", n_features=0)
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_max_frac_repeated_parameter():
    """Assert that an error is raised when max_frac_repeated is invalid."""
    fs = FeatureSelector(strategy=None, max_frac_repeated=1.1)
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_max_correlation_parameter():
    """Assert that an error is raised when max_correlation is invalid."""
    fs = FeatureSelector(strategy=None, max_correlation=-0.2)
    pytest.raises(ValueError, fs.fit, X_reg, y_reg)


def test_error_y_is_None():
    """Assert that an error is raised when y is None for some strategies."""
    fs = FeatureSelector(strategy="univariate", solver=f_regression, n_features=9)
    pytest.raises(ValueError, fs.fit, X_reg)


def test_remove_low_variance():
    """Assert that the remove_low_variance function works as intended."""
    X = X_bin.copy()
    X["invalid"] = 3  # Add column with minimum variance
    fs = FeatureSelector(max_frac_repeated=1.0)
    X = fs.fit_transform(X)
    assert X.shape[1] == X_bin.shape[1]


def test_collinear_attribute():
    """Assert that the collinear attribute is created."""
    fs = FeatureSelector(max_correlation=0.6)
    assert hasattr(fs, "collinear")


def test_remove_collinear():
    """Assert that the remove_collinear function works as intended."""
    fs = FeatureSelector(max_correlation=0.9)
    X = fs.fit_transform(X_bin)
    assert X.shape[1] == 20  # Originally 30


def test_univariate_strategy_custom_solver():
    """Assert that the univariate strategy works for a custom solver."""
    fs = FeatureSelector("univariate", solver=f_regression, n_features=9)
    X = fs.fit_transform(X_reg, y_reg)
    assert X.shape[1] == 9
    assert set(fs.feature_importance) == set(X.columns)


def test_PCA_strategy():
    """Assert that the PCA strategy works as intended."""
    fs = FeatureSelector(strategy="PCA", n_features=0.7)
    X = fs.fit_transform(X_bin)
    assert X.shape[1] == 21


def test_PCA_components():
    """Assert that the PCA strategy creates components instead of features."""
    fs = FeatureSelector(strategy="PCA")
    X = fs.fit_transform(X_bin)
    assert "Component 1" in X.columns


def test_SFM_prefit_invalid_estimator():
    """Assert that an error is raised for an invalid estimator in SFM."""
    fs = FeatureSelector(
        strategy="SFM",
        solver=ExtraTreesClassifier(random_state=1).fit(X_class, y_class),
        n_features=8,
        random_state=1,
    )
    pytest.raises(ValueError, fs.fit, X_bin, y_bin)


def test_SFM_strategy_not_threshold():
    """Assert that if threshold is not specified, SFM selects n_features features."""
    fs = FeatureSelector(
        strategy="SFM",
        solver=ExtraTreesClassifier(random_state=1),
        n_features=16,
        random_state=1,
    )
    X = fs.fit_transform(X_bin, y_bin)
    assert X.shape[1] == 16


def test_SFM_invalid_solver():
    """Assert that an error is raised when solver is invalid."""
    fs = FeatureSelector(strategy="SFM", solver="invalid", n_features=5)
    pytest.raises(ValueError, fs.fit_transform, X_bin, y_bin)


def test_SFM_strategy_fitted_solver():
    """Assert that the SFM strategy works when the solver is already fitted."""
    fs = FeatureSelector(
        strategy="SFM",
        solver=ExtraTreesClassifier(random_state=1).fit(X_bin, y_bin),
        n_features=7,
        random_state=1,
    )
    X = fs.fit_transform(X_bin)
    assert X.shape[1] == 7
    assert set(fs.feature_importance) == set(X.columns)


def test_SFM_strategy_not_fitted_solver():
    """Assert that the SFM strategy works when the solver is not fitted."""
    fs = FeatureSelector(
        strategy="SFM", solver=ExtraTreesClassifier(random_state=1), n_features=5
    )
    X = fs.fit_transform(X_bin, y_bin)
    assert X.shape[1] == 5
    assert set(fs.feature_importance) == set(X.columns)


def test_RFE_strategy():
    """Assert that the RFE strategy works as intended."""
    fs = FeatureSelector(
        strategy="RFE",
        solver=ExtraTreesClassifier(random_state=1),
        n_features=13,
        random_state=1,
    )
    X = fs.fit_transform(X_bin, y_bin)
    assert X.shape[1] == 13
    assert set(fs.feature_importance) == set(X.columns)


def test_RFECV_strategy_before_pipeline_classification():
    """Assert that the RFECV strategy works before a fitted pipeline."""
    fs = FeatureSelector("RFECV", solver="RF_class", n_features=None, random_state=1)
    X = fs.fit_transform(X_bin, y_bin)
    assert X.shape[1] == 17
    assert set(fs.feature_importance) == set(X.columns)


def test_RFECV_strategy_before_pipeline_regression():
    """Assert that the RFECV strategy works before a fitted pipeline."""
    fs = FeatureSelector("RFECV", solver="RF_reg", n_features=16, random_state=1)
    X = fs.fit_transform(X_reg, y_reg)
    assert X.shape[1] == 10
    assert set(fs.feature_importance) == set(X.columns)


def test_SFS_strategy():
    """Assert that the SFS strategy works."""
    fs = FeatureSelector("SFS", solver="RF_reg", n_features=6, cv=3, random_state=1)
    X = fs.fit_transform(X_reg, y_reg)
    assert X.shape[1] == 6


def test_kwargs_parameter_threshold():
    """Assert that the kwargs parameter works as intended (add threshold)."""
    fs = FeatureSelector(
        strategy="SFM",
        solver=ExtraTreesClassifier(random_state=1),
        n_features=21,
        threshold="mean",
        random_state=1,
    )
    X = fs.fit_transform(X_bin, y_bin)
    assert X.shape[1] == 10


def test_kwargs_parameter_tol():
    """Assert that the kwargs parameter works as intended (add tol)."""
    fs = FeatureSelector(
        strategy="PCA", solver="arpack", tol=0.001, n_features=12, random_state=1
    )
    X = fs.fit_transform(X_bin)
    assert X.shape[1] == 12


def test_kwargs_parameter_scoring():
    """Assert that the kwargs parameter works as intended (add scoring acronym)."""
    fs = FeatureSelector(
        strategy="RFECV",
        solver="rf_class",
        scoring="auc",
        n_features=12,
        random_state=1,
    )
    X = fs.fit_transform(X_bin, y_bin)
    assert X.shape[1] == 14
