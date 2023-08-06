import numpy as np, pandas as pd
from scipy.sparse import csc_matrix, csr_matrix, issparse, isspmatrix_csc, isspmatrix_csr, vstack as sp_vstack
import warnings
import multiprocessing
import ctypes
import json
from copy import deepcopy
from ._cpp_interface import isoforest_cpp_obj, _sort_csc_indices, _reconstruct_csr_sliced, _reconstruct_csr_with_categ

__all__ = ["IsolationForest"]

### Helpers
def _get_num_dtype(X_num=None, sample_weights=None, column_weights=None):
    if X_num is not None:
        return np.empty(0, dtype=X_num.dtype)
    elif sample_weights is not None:
        return np.empty(0, dtype=column_weights.dtype)
    elif column_weights is not None:
        return np.empty(0, dtype=sample_weights.dtype)
    else:
        return np.empty(0, dtype=ctypes.c_double)

def _get_int_dtype(X_num):
    if (X_num is not None) and (issparse(X_num)):
        return np.empty(0, dtype=X_num.indices.dtype)
    else:
        return np.empty(0, dtype=ctypes.c_size_t)

def _is_row_major(X_num):
    if (X_num is None) or (issparse(X_num)):
        return False
    else:
        return X_num.strides[1] == X_num.dtype.itemsize

def _is_col_major(X_num):
    if (X_num is None) or (issparse(X_num)):
        return False
    else:
        return X_num.strides[0] == X_num.dtype.itemsize

def _copy_if_subview(X_num):
    ### TODO: the C++ functions should accept a 'leading dimension'
    ### parameter so as to avoid copying the data here
    if (X_num is not None) and (not issparse(X_num)):
        col_major = _is_col_major(X_num)
        leading_dimension = int(X_num.strides[1 if col_major else 0] / X_num.dtype.itemsize)
        if (
                (leading_dimension != X_num.shape[0 if col_major else 1]) or
                (len(X_num.strides) != 2) or
                (not X_num.flags.aligned) or
                (not _is_row_major(X_num) and not _is_col_major(X_num))
            ):
            X_num = X_num.copy()
        if _is_col_major(X_num) != col_major:
            X_num = np.asfortranarray(X_num)
    return X_num

class IsolationForest:
    """
    Isolation Forest model

    Isolation Forest is an algorithm originally developed for outlier detection that consists in splitting
    sub-samples of the data according to some attribute/feature/column at random. The idea is that, the rarer
    the observation, the more likely it is that a random uniform split on some feature would put outliers alone
    in one branch, and the fewer splits it will take to isolate an outlier observation like this. The concept
    is extended to splitting hyperplanes in the extended model (i.e. splitting by more than one column at a time), and to
    guided (not entirely random) splits in the SCiForest model that aim at isolating outliers faster and
    finding clustered outliers.

    This version adds heuristics to handle missing data and categorical variables. Can be used to aproximate pairwise
    distances by checking the depth after which two observations become separated, and to approximate densities by fitting
    trees beyond balanced-tree limit. Offers options to vary between randomized and deterministic splits too.

    Note
    ----
    The default parameters in this software do not correspond to the suggested parameters in
    any of the references.
    In particular, the following default values are likely to cause huge differences when compared to the
    defaults in other software: ``ndim``, ``sample_size``, ``ntrees``. The defaults here are
    nevertheless more likely to result in better models. In order to mimic scikit-learn for example, one
    would need to pass ``ndim=1``, ``sample_size=256``, ``ntrees=100``, ``missing_action="fail"``, ``nthreads=1``.

    Note
    ----
    The model offers many tunable parameters. The most likely candidate to tune is
    ``prob_pick_pooled_gain``, for which higher values tend to
    result in a better ability to flag outliers in the training data at the expense of hindered
    performance when making predictions on new data (calling method ``predict``) and poorer
    generalizability to inputs with values outside the variables' ranges to which the model was fit
    (see plots generated from the examples in GitHub notebook for a better idea of the difference). The next candidate to tune is
    ``sample_size`` - the default is to use all rows, but in some datasets introducing sub-sampling can help,
    especially for the single-variable model. In smaller datasets, one might also want to experiment
    with ``weigh_by_kurtosis`` and perhaps lower ``ndim``.

    Note
    ----
    The default parameters will not scale to large datasets. In particular,
    if the amount of data is large, it's suggested to set a smaller sample size for each tree (parameter ``sample_size``)
    and to fit fewer of them (parameter ``ntrees``).
    As well, the default option for 'missing_action' might slow things down significantly.
    See the documentation of the parameters for more details.
    These defaults can also result in very big model sizes in memory and as serialized
    files (e.g. models that weight over 10GB) when the number of rows in the data is large.
    Using fewer trees, smaller sample sizes, and shallower trees can help to reduce model
    sizes if that becomes a problem.

    Note
    ----
    When using more than one dimension for splits (i.e. splitting hyperplanes, see ``ndim``) and when
    calculating gain, the variables are standardized at each step, so there is no need to center/scale the
    data beforehand. The gain calculations are also standardized according to the standard deviation when
    using ``ntry>1`` or ``ndim==1``, in order to avoid differences in the magnitudes of the coefficients.

    Parameters
    ----------
    sample_size : int, float(0,1), or None
        Sample size of the data sub-samples with which each binary tree will be built. If passing 'None', each
        tree will be built using the full data. Recommended value in [1], [2], [3] is 256, while
        the default value in the author's code in [5] is 'None' here.

        If passing a number between zero and one, will assume it means taking a sample size that represents
        that proportion of the rows in the data.

        Hint: seeing a distribution of scores which is on average too far below 0.5 could mean that the
        model needs more trees and/or bigger samples to reach convergence (unless using non-random
        splits, in which case the distribution is likely to be centered around a much lower number),
        or that the distributions in the data are too skewed for random uniform splits.
    ntrees : int
        Number of binary trees to build for the model. Recommended value in [1] is 100, while the default value in the
        author's code in [5] is 10. In general, the number of trees required for good results
        is higher when (a) there are many columns, (b) there are categorical variables, (c) categorical variables have many
        categories, (d) `ndim` is high.

        Hint: seeing a distribution of scores which is on average too far below 0.5 could mean that the
        model needs more trees and/or bigger samples to reach convergence (unless using non-random
        splits, in which case the distribution is likely to be centered around a much lower number),
        or that the distributions in the data are too skewed for random uniform splits.
    ndim : int
        Number of columns to combine to produce a split. If passing 1, will produce the single-variable model described
        in [1] and [2], while if passing values greater than 1, will produce the extended model described in [3] and [4].
        Recommended value in [4] is 2, while [3] recommends a low value such as 2 or 3. Models with values higher than 1
        are referred hereafter as the extended model (as in [3]).

        Note that, when using ``ndim>1``, the variables are standardized at each step as suggested in [4],
        which makes the models slightly different than in [3].
    ntry : int
        In the extended model with non-random splits, how many random combinations to try for determining the best gain.
        Only used when deciding splits by gain (see documentation for parameters 'prob_pick_avg_gain' and 'prob_pick_pooled_gain').
        Recommended value in [4] is 10. Ignored for single-variable model.
    categ_cols : None or array-like
        Columns that hold categorical features, when the data is passed as an array or matrix.
        Categorical columns should contain only integer values with a continuous numeration starting at zero,
        with negative values and NaN taken as missing,
        and the array or list passed here should correspond to the column numbers, with numeration starting
        at zero.
        This might be passed either at construction time or when calling ``fit`` or variations of ``fit``.
        
        This is ignored when the input is passed as a ``DataFrame`` as then it will consider columns as
        categorical depending on their dtype (see the documentation for ``fit`` for details).
    max_depth : int, None, or str "auto"
        Maximum depth of the binary trees to grow. If passing None, will build trees until each observation ends alone
        in a terminal node or until no further split is possible. If using "auto", will limit it to the corresponding
        depth of a balanced binary tree with number of terminal nodes corresponding to the sub-sample size (the reason
        being that, if trying to detect outliers, an outlier will only be so if it turns out to be isolated with shorter average
        depth than usual, which corresponds to a balanced tree depth). When a terminal node has more than 1 observation, the
        remaining isolation depth for them is estimated assuming the data and splits are both uniformly random (separation depth
        follows a similar process with expected value calculated as in [6]). Default setting for [1], [2], [3], [4] is "auto",
        but it's recommended to pass higher values if using the model for purposes other than outlier detection.
    ncols_per_tree : None, int, or float(0,1)
        Number of columns to use (have as potential candidates for splitting at each iteration) in each tree,
        somewhat similar to the 'mtry' parameter of random forests.
        In general, this is only relevant when using non-random splits and/or weighting by kurtosis.

        If passing a number between zero and one, will assume it means taking a sample size that represents
        that proportion of the columns in the data.

        If passing ``None`` (the default), will use the full number of available columns.
    prob_pick_avg_gain : float(0, 1)
        * For the single-variable model (``ndim=1``), this parameter indicates the probability
          of making each split by choosing a column and split point in that
          same column as both the column and split point that gives the largest averaged gain (as proposed in [4]) across
          all available columns and possible splits in each column. Note that this implies evaluating every single column
          in the sample data when this type of split happens, which will potentially make the model fitting much slower,
          but has no impact on prediction time. For categorical variables, will take the expected standard deviation that
          would be gotten if the column were converted to numerical by assigning to each category a random number ~ Unif(0, 1)
          and calculate gain with those assumed standard deviations.
        
        * For the extended model, this parameter indicates the probability that the
          split point in the chosen linear combination of variables will be decided by this averaged gain criterion.

        Compared to a pooled average, this tends to result in more cases in which a single observation or very few of them
        are put into one branch. Recommended to use sub-samples (parameter 'sample_size') when passing this parameter.
        Note that, since this will created isolated nodes faster, the resulting object will be lighter (use less memory).
        
        When splits are
        not made according to any of 'prob_pick_avg_gain', 'prob_pick_pooled_gain', 'prob_split_avg_gain',
        'prob_split_pooled_gain', both the column and the split point are decided at random. Default setting for [1], [2], [3] is
        zero, and default for [4] is 1. This is the randomization parameter that can be passed to the author's original code in [5],
        but note that the code in [5] suffers from a mathematical error in the calculation of running standard deviations,
        so the results from it might not match with this library's.
        
        Note that, if passing a value of 1 (100%) with no sub-sampling and using the single-variable model, every single tree will have
        the exact same splits.

        Important detail: if using either ``prob_pick_avg_gain`` or ``prob_pick_pooled_gain``, the distribution of
        outlier scores is unlikely to be centered around 0.5.
    prob_pick_pooled_gain : float(0, 1)
        * For the single-variable model (``ndim=1``), this parameter indicates the probability
          of making each split by choosing a column and split point in that
          same column as both the column and split point that gives the largest pooled gain (as used in decision tree
          classifiers such as C4.5 in [7]) across all available columns and possible splits in each column. Note
          that this implies evaluating every single column in the sample data when this type of split happens, which
          will potentially make the model fitting much slower, but has no impact on prediction time. For categorical
          variables, will use shannon entropy instead (like in [7]).
        
        * For the extended model, this parameter indicates the probability
          that the split point in the chosen linear combination of variables will be decided by this pooled gain
          criterion.

        Compared to a simple average, this tends to result in more evenly-divided splits and more clustered
        groups when they are smaller. Recommended to pass higher values when used for imputation of missing values.
        When used for outlier detection, higher values of this parameter result in models that are able to better flag
        outliers in the training data of each tree, but generalize poorly to outliers in new data and to values of variables
        outside of the ranges from the training data. Passing small 'sample_size' and high values of this parameter will
        tend to flag too many outliers.
        
        Note that, since this makes the trees more even and thus it takes more steps to produce isolated nodes,
        the resulting object will be heavier. When splits are not made according to any of 'prob_pick_avg_gain',
        'prob_pick_pooled_gain', 'prob_split_avg_gain', 'prob_split_pooled_gain', both the column and the split point
        are decided at random. Note that, if passing value 1 (100%) with no sub-sampling and using the single-variable model,
        every single tree will have the exact same splits.

        Be aware that ``penalize_range`` can also have a large impact when using ``prob_pick_pooled_gain``.

        Important detail: if using either ``prob_pick_avg_gain`` or ``prob_pick_pooled_gain``, the distribution of
        outlier scores is unlikely to be centered around 0.5.
    prob_split_avg_gain : float(0, 1)
        Probability of making each split by selecting a column at random and determining the split point as
        that which gives the highest averaged gain. Not supported for the extended model as the splits are on
        linear combinations of variables. See the documentation for parameter 'prob_pick_avg_gain' for more details.
    prob_split_pooled_gain : float(0, 1)
        Probability of making each split by selecting a column at random and determining the split point as
        that which gives the highest pooled gain. Not supported for the extended model as the splits are on
        linear combinations of variables. See the documentation for parameter 'prob_pick_pooled_gain' for more details.
    min_gain : float > 0
        Minimum gain that a split threshold needs to produce in order to proceed with a split. Only used when the splits
        are decided by a gain criterion (either pooled or averaged). If the highest possible gain in the evaluated
        splits at a node is below this  threshold, that node becomes a terminal node.
    missing_action : str, one of "divide" (single-variable only), "impute", "fail", "auto"
        How to handle missing data at both fitting and prediction time. Options are:
        
        ``"divide"``:
            (For the single-variable model only, recommended) Will follow both branches and combine the result with the
            weight given by the fraction of the data that went to each branch when fitting the model.
        ``"impute"``:
            Will assign observations to the branch with the most observations in the single-variable model, or fill in
            missing values with the median of each column of the sample from which the split was made in the extended
            model (recommended for the extended model).
        ``"fail"``:
            Will assume there are no missing values and will trigger undefined behavior if it encounters any.
        ``"auto"``:
            Will use "divide" for the single-variable model and "impute" for the extended model.
        
        In the extended model, infinite values will be treated as missing.
        Passing "fail" will produce faster fitting and prediction times along with decreased
        model object sizes.
        Models from [1], [2], [3], [4] correspond to "fail" here.
    new_categ_action : str, one of "weighted" (single-variable only), "impute" (extended only), "smallest", "random"
        What to do after splitting a categorical feature when new data that reaches that split has categories that
        the sub-sample from which the split was done did not have. Options are:

        ``"weighted"``:
            (For the single-variable model only, recommended) Will follow both branches and combine the result with weight given
            by the fraction of the data that went to each branch when fitting the model.
        ``"impute"``:
            (For the extended model only, recommended) Will assign them the median value for that column that was added to the linear
            combination of features.
        ``"smallest"``:
            In the single-variable case will assign all observations with unseen categories in the split to the branch that had
            fewer observations when fitting the model, and in the extended case will assign them the coefficient of the least
            common category.
        ``"random"``:
            Will assing a branch (coefficient in the extended model) at random for each category beforehand, even if no observations
            had that category when fitting the model.
        ``"auto"``:
            Will select "weighted" for the single-variable model and "impute" for the extended model.
        Ignored when passing 'categ_split_type' = 'single_categ'.
    categ_split_type : str, one of "subset" or "single_categ"
        Whether to split categorical features by assigning sub-sets of them to each branch, or by assigning
        a single category to a branch and the rest to the other branch. For the extended model, whether to
        give each category a coefficient, or only one while the rest get zero.
    all_perm : bool
        When doing categorical variable splits by pooled gain with ``ndim=1`` (regular model),
        whether to consider all possible permutations of variables to assign to each branch or not. If ``False``,
        will sort the categories by their frequency and make a grouping in this sorted order. Note that the
        number of combinations evaluated (if ``True``) is the factorial of the number of present categories in
        a given column (minus 2). For averaged gain, the best split is always to put the second most-frequent
        category in a separate branch, so not evaluating all  permutations (passing ``False``) will make it
        possible to select other splits that respect the sorted frequency order.
        Ignored when not using categorical variables or not doing splits by pooled gain or using ``ndim > 1``.
    coef_by_prop : bool
        In the extended model, whether to sort the randomly-generated coefficients for categories
        according to their relative frequency in the tree node. This might provide better results when using
        categorical variables with too many categories, but is not recommended, and not reflective of
        real "categorical-ness". Ignored for the regular model (``ndim=1``) and/or when not using categorical
        variables.
    recode_categ : bool
        Whether to re-encode categorical variables even in case they are already passed
        as ``pd.Categorical``. This is recommended as it will eliminate potentially redundant categorical levels if
        they have no observations, but if the categorical variables are already of type ``pd.Categorical`` with only
        the levels that are present, it can be skipped for slightly faster fitting times. You'll likely
        want to pass ``False`` here if merging several models into one through ``append_trees``.
    weights_as_sample_prob : bool
        If passing sample (row) weights when fitting the model, whether to consider those weights as row
        sampling weights (i.e. the higher the weights, the more likely the observation will end up included
        in each tree sub-sample), or as distribution density weights (i.e. putting a weight of two is the same
        as if the row appeared twice, thus higher weight makes it less of an outlier). Note that sampling weight
        is only used when sub-sampling data for each tree, which is not the default in this implementation.
    sample_with_replacement : bool
        Whether to sample rows with replacement or not (not recommended). Note that distance calculations,
        if desired, don't work well with duplicate rows.
    penalize_range : bool
        Whether to penalize (add -1 to the terminal depth) observations at prediction time that have a value
        of the chosen split variable (linear combination in extended model) that falls outside of a pre-determined
        reasonable range in the data being split (given by 2 * range in data and centered around the split point),
        as proposed in [4] and implemented in the authors' original code in [5]. Not used in single-variable model
        when splitting by categorical variables.

        It's recommended to turn this off for faster predictions on sparse CSC matrices.

        Note that this can make a very large difference in the results when using ``prob_pick_pooled_gain``.

        Be aware that this option can make the distribution of outlier scores a bit different
        (i.e. not centered around 0.5)
    weigh_by_kurtosis : bool
        Whether to weigh each column according to the kurtosis obtained in the sub-sample that is selected
        for each tree as briefly proposed in [1]. Note that this is only done at the beginning of each tree
        sample, so if not using sub-samples, it's better to pass column weights calculated externally. For
        categorical columns, will calculate expected kurtosis if the column was converted to numerical by
        assigning to each category a random number ~ Unif(0, 1).

        Note that when using sparse matrices, the calculation of kurtosis will rely on a procedure that
        uses sums of squares and higher-power numbers, which has less numerical precision than the
        calculation used for dense inputs, and as such, the results might differ slightly.

        Using this option makes the model more likely to pick the columns that have anomalous values
        when viewed as a 1-d distribution, and can bring a large improvement in some datasets.
    coefs : str, one of "normal" or "uniform"
        For the extended model, whether to sample random coefficients according to a normal distribution ~ N(0, 1)
        (as proposed in [3]) or according to a uniform distribution ~ Unif(-1, +1) as proposed in [4]. Ignored for the
        single-variable model. Note that, for categorical variables, the coefficients will be sampled ~ N (0,1)
        regardless - in order for both types of variables to have transformations in similar ranges (which will tend
        to boost the importance of categorical variables), pass ``"uniform"`` here.
    assume_full_distr : bool
        When calculating pairwise distances (see [8]), whether to assume that the fitted model represents
        a full population distribution (will use a standardizing criterion assuming infinite sample,
        and the results of the similarity between two points at prediction time will not depend on the
        prescence of any third point that is similar to them, but will differ more compared to the pairwise
        distances between points from which the model was fit). If passing 'False', will calculate pairwise distances
        as if the new observations at prediction time were added to the sample to which each tree was fit, which
        will make the distances between two points potentially vary according to other newly introduced points.
        This will not be assumed when the distances are calculated as the model is being fit (see documentation
        for method 'fit_transform').
    build_imputer : bool
        Whether to construct missing-value imputers so that later this same model could be used to impute
        missing values of new (or the same) observations. Be aware that this will significantly increase the memory
        requirements and serialized object sizes. Note that this is not related to 'missing_action' as missing
        values inside the model are treated differently and follow their own imputation or division strategy.
    min_imp_obs : int
        Minimum number of observations with which an imputation value can be produced. Ignored if passing
        'build_imputer' = 'False'.
    depth_imp : str, one of "higher", "lower", "same"
        How to weight observations according to their depth when used for imputing missing values. Passing
        "higher" will weigh observations higher the further down the tree (away from the root node) the
        terminal node is, while "lower" will do the opposite, and "same" will not modify the weights according
        to node depth in the tree. Implemented for testing purposes and not recommended to change
        from the default. Ignored when passing 'build_imputer' = 'False'.
    weigh_imp_rows : str, one of "inverse", "prop", "flat"
        How to weight node sizes when used for imputing missing values. Passing "inverse" will weigh
        a node inversely proportional to the number of observations that end up there, while "proportional"
        will weight them heavier the more observations there are, and "flat" will weigh all nodes the same
        in this regard regardless of how many observations end up there. Implemented for testing purposes
        and not recommended to change from the default. Ignored when passing 'build_imputer' = 'False'.
    random_seed : int
        Seed that will be used for random number generation.
    nthreads : int
        Number of parallel threads to use. If passing a negative number, will use
        the same formula as joblib does for calculating number of threads (which is
        n_cpus + 1 + n_jobs - i.e. pass -1 to use all available threads). Note that, the more threads,
        the more memory will be allocated, even if the thread does not end up being used.
        Be aware that most of the operations are bound by memory bandwidth, which means that
        adding more threads will not result in a linear speed-up. For some types of data
        (e.g. large sparse matrices with small sample sizes), adding more threads might result
        in only a very modest speed up (e.g. 1.5x faster with 4x more threads),
        even if all threads look fully utilized.
    n_estimators : None or int
        Synonym for ``ntrees``, kept for better compatibility with scikit-learn.
    max_samples : None or int
        Synonym for ``sample_size``, kept for better compatibility with scikit-learn.
    n_jobs : None or int
        Synonym for ``nthreads``, kept for better compatibility with scikit-learn.
    random_state : None, int, or RandomState
        Synonym for ``random_seed``, kept for better compatibility with scikit-learn.
    bootstrap : None or bool
        Synonym for ``sample_with_replacement``, kept for better compatibility with scikit-learn.

    Attributes
    ----------
    cols_numeric_ : array(n_num_features,)
        Array with the names of the columns that were taken as numerical
        (Only when fitting the model to a DataFrame object).
    cols_categ_ : array(n_categ_features,)
        Array with the names of the columns that were taken as categorical
        (Only when fitting the model to a DataFrame object).
    is_fitted_ : bool
        Indicator telling whether the model has been fit to data or not.

    References
    ----------
    .. [1] Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou. "Isolation forest."
           2008 Eighth IEEE International Conference on Data Mining. IEEE, 2008.
    .. [2] Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou. "Isolation-based anomaly detection."
           ACM Transactions on Knowledge Discovery from Data (TKDD) 6.1 (2012): 3.
    .. [3] Hariri, Sahand, Matias Carrasco Kind, and Robert J. Brunner. "Extended Isolation Forest."
           arXiv preprint arXiv:1811.02141 (2018).
    .. [4] Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou. "On detecting clustered anomalies using SCiForest."
           Joint European Conference on Machine Learning and Knowledge Discovery in Databases. Springer, Berlin, Heidelberg, 2010.
    .. [5] https://sourceforge.net/projects/iforest/
    .. [6] https://math.stackexchange.com/questions/3388518/expected-number-of-paths-required-to-separate-elements-in-a-binary-tree
    .. [7] Quinlan, J. Ross. C4. 5: programs for machine learning. Elsevier, 2014.
    .. [8] Cortes, David. "Distance approximation using Isolation Forests."
           arXiv preprint arXiv:1910.12362 (2019).
    .. [9] Cortes, David. "Imputing missing values with unsupervised random trees."
           arXiv preprint arXiv:1911.06646 (2019).
    .. [10] https://math.stackexchange.com/questions/3333220/expected-average-depth-in-random-binary-tree-constructed-top-to-bottom
    """
    def __init__(self, sample_size = None, ntrees = 500, ndim = 3, ntry = 3,
                 categ_cols = None, max_depth = "auto", ncols_per_tree = None,
                 prob_pick_avg_gain = 0.0, prob_pick_pooled_gain = 0.0,
                 prob_split_avg_gain = 0.0, prob_split_pooled_gain = 0.0,
                 min_gain = 0., missing_action = "auto", new_categ_action = "auto",
                 categ_split_type = "subset", all_perm = False,
                 coef_by_prop = False, recode_categ = True,
                 weights_as_sample_prob = True, sample_with_replacement = False,
                 penalize_range = False, weigh_by_kurtosis = False,
                 coefs = "normal", assume_full_distr = True,
                 build_imputer = False, min_imp_obs = 3,
                 depth_imp = "higher", weigh_imp_rows = "inverse",
                 random_seed = 1, nthreads = -1,
                 n_estimators = None, max_samples = None,
                 n_jobs = None, random_state = None, bootstrap = None):
        self.sample_size = sample_size
        self.ntrees = ntrees
        self.ndim = ndim
        self.ntry = ntry
        self.categ_cols = categ_cols
        self.max_depth = max_depth
        self.ncols_per_tree = ncols_per_tree
        self.prob_pick_avg_gain = prob_pick_avg_gain
        self.prob_pick_pooled_gain = prob_pick_pooled_gain
        self.prob_split_avg_gain = prob_split_avg_gain
        self.prob_split_pooled_gain = prob_split_pooled_gain
        self.min_gain = min_gain
        self.missing_action = missing_action
        self.new_categ_action = new_categ_action
        self.categ_split_type = categ_split_type
        self.all_perm = all_perm
        self.coef_by_prop = coef_by_prop
        self.recode_categ = recode_categ
        self.weights_as_sample_prob = weights_as_sample_prob
        self.sample_with_replacement = sample_with_replacement
        self.penalize_range = penalize_range
        self.weigh_by_kurtosis = weigh_by_kurtosis
        self.coefs = coefs
        self.assume_full_distr = assume_full_distr
        self.build_imputer = build_imputer
        self.min_imp_obs = min_imp_obs
        self.depth_imp = depth_imp
        self.weigh_imp_rows = weigh_imp_rows
        self.random_seed = random_seed
        self.nthreads = nthreads
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.bootstrap = bootstrap

        self._reset_obj()

    def _init(self, categ_cols = None):
        if categ_cols is not None:
            if self.categ_cols is not None:
                warnings.warn("Passed 'categ_cols' in constructor and fit method. Will take the latter.")
            self.categ_cols = categ_cols
        self._initialize_full(
                 sample_size = self.sample_size if (self.max_samples is None) else self.max_samples,
                 ntrees = self.ntrees if (self.n_estimators is None) else self.n_estimators,
                 ndim = self.ndim, ntry = self.ntry,
                 categ_cols = self.categ_cols,
                 max_depth = self.max_depth, ncols_per_tree = self.ncols_per_tree,
                 prob_pick_avg_gain = self.prob_pick_avg_gain, prob_pick_pooled_gain = self.prob_pick_pooled_gain,
                 prob_split_avg_gain = self.prob_split_avg_gain, prob_split_pooled_gain = self.prob_split_pooled_gain,
                 min_gain = self.min_gain, missing_action = self.missing_action, new_categ_action = self.new_categ_action,
                 categ_split_type = self.categ_split_type, all_perm = self.all_perm,
                 coef_by_prop = self.coef_by_prop, recode_categ = self.recode_categ,
                 weights_as_sample_prob = self.weights_as_sample_prob,
                 sample_with_replacement = self.sample_with_replacement if (self.bootstrap is None) else self.bootstrap,
                 penalize_range = self.penalize_range, weigh_by_kurtosis = self.weigh_by_kurtosis,
                 coefs = self.coefs, assume_full_distr = self.assume_full_distr,
                 build_imputer = self.build_imputer, min_imp_obs = self.min_imp_obs,
                 depth_imp = self.depth_imp, weigh_imp_rows = self.weigh_imp_rows,
                 random_seed = self.random_seed if (self.random_state is None) else self.random_state,
                 nthreads = self.nthreads if (self.n_jobs is None) else self.n_jobs)

    def _initialize_full(self, sample_size = None, ntrees = 500, ndim = 3, ntry = 3,
                 categ_cols = None, max_depth = "auto", ncols_per_tree = None,
                 prob_pick_avg_gain = 0.0, prob_pick_pooled_gain = 0.0,
                 prob_split_avg_gain = 0.0, prob_split_pooled_gain = 0.0,
                 min_gain = 0., missing_action = "auto", new_categ_action = "auto",
                 categ_split_type = "subset", all_perm = False,
                 coef_by_prop = False, recode_categ = True,
                 weights_as_sample_prob = True, sample_with_replacement = False,
                 penalize_range = True, weigh_by_kurtosis = False,
                 coefs = "normal", assume_full_distr = True,
                 build_imputer = False, min_imp_obs = 3,
                 depth_imp = "higher", weigh_imp_rows = "inverse",
                 random_seed = 1, nthreads = -1):
        if sample_size is not None:
            assert sample_size > 0
            if sample_size > 1:
                assert isinstance(sample_size, int)
            elif sample_size == 1:
                sample_size = None
        if ncols_per_tree is not None:
            assert ncols_per_tree > 0
            if ncols_per_tree > 1:
                assert isinstance(ncols_per_tree, int)
            elif ncols_per_tree == 1:
                ncols_per_tree = None
        assert ntrees > 0
        assert isinstance(ntrees, int)
        if (max_depth != "auto") and (max_depth is not None):
            assert max_depth > 0
            assert isinstance(max_depth, int)
            if sample_size is not None:
                assert max_depth < sample_size
        assert ndim >= 1
        assert isinstance(ndim, int)
        assert ntry >= 1
        assert isinstance(ntry, int)
        if isinstance(random_seed, np.random.RandomState):
            random_seed = random_seed.randint(np.iinfo(np.int32).max)
        if isinstance(random_seed, np.random.Generator):
            random_seed = random_seed.integers(np.iinfo(np.int32).max)
        random_seed = int(random_seed)
        assert random_seed >= 0
        assert isinstance(min_imp_obs, int)
        assert min_imp_obs >= 1

        assert missing_action    in ["divide",        "impute",   "fail",   "auto"]
        assert new_categ_action  in ["weighted",      "smallest", "random", "impute", "auto"]
        assert categ_split_type  in ["single_categ",  "subset"]
        assert coefs             in ["normal",        "uniform"]
        assert depth_imp         in ["lower",         "higher",   "same"]
        assert weigh_imp_rows    in ["inverse",       "prop",     "flat"]

        assert prob_pick_avg_gain     >= 0
        assert prob_pick_pooled_gain  >= 0
        assert prob_split_avg_gain    >= 0
        assert prob_split_pooled_gain >= 0
        assert min_gain               >= 0
        s = prob_pick_avg_gain + prob_pick_pooled_gain + prob_split_avg_gain + prob_split_pooled_gain
        if s > 1:
            warnings.warn("Split type probabilities sum to more than 1, will standardize them")
            prob_pick_avg_gain     /= s
            prob_pick_pooled_gain  /= s
            prob_split_avg_gain    /= s
            prob_split_pooled_gain /= s

        if (ndim == 1) and (sample_size is None) and ((prob_pick_avg_gain >= 1) or (prob_pick_pooled_gain >= 1)) and (not sample_with_replacement):
            msg  = "Passed parameters for deterministic single-variable splits"
            msg += " with no sub-sampling. "
            msg += "Every tree fitted will end up doing exactly the same splits. "
            msg += "It's recommended to set 'prob_pick_avg_gain' < 1, 'prob_pick_pooled_gain' < 1, "
            msg += "or to use the extended model (ndim > 1)."
            warnings.warn(msg)

        if missing_action == "auto":
            if ndim == 1:
                missing_action = "divide"
            else:
                missing_action = "impute"

        if new_categ_action == "auto":
            if ndim == 1:
                new_categ_action = "weighted"
            else:
                new_categ_action = "impute"

        if (build_imputer) and (missing_action == "fail"):
            raise ValueError("Cannot impute missing values when passing 'missing_action' = 'fail'.")

        if ndim == 1:
            if new_categ_action == "impute":
                raise ValueError("'new_categ_action' = 'impute' not supported in single-variable model.")
        else:
            if (prob_split_avg_gain > 0) or (prob_split_pooled_gain > 0):
                msg  = "Non-zero values for 'prob_split_avg_gain' "
                msg += "and 'prob_split_pooled_gain' not meaningful in "
                msg += "extended model."
                raise ValueError(msg)
            if missing_action == "divide":
                raise ValueError("'missing_action' = 'divide' not supported in extended model.")
            if new_categ_action == "weighted":
                raise ValueError("'new_categ_action' = 'weighted' not supported in extended model.")

        if nthreads is None:
            nthreads = 1
        elif nthreads < 0:
            nthreads = multiprocessing.cpu_count() + 1 + nthreads

        assert nthreads > 0
        assert isinstance(nthreads, int)

        if categ_cols is not None:
            categ_cols = np.array(categ_cols).reshape(-1).astype(int)
            categ_cols.sort()

        self.sample_size             =  sample_size
        self.ntrees                  =  ntrees
        self.ndim                    =  ndim
        self.ntry                    =  ntry
        self.categ_cols              =  categ_cols
        self.max_depth               =  max_depth
        self.ncols_per_tree          =  ncols_per_tree
        self.prob_pick_avg_gain      =  prob_pick_avg_gain
        self.prob_pick_pooled_gain   =  prob_pick_pooled_gain
        self.prob_split_avg_gain     =  prob_split_avg_gain
        self.prob_split_pooled_gain  =  prob_split_pooled_gain
        self.min_gain                =  min_gain
        self.missing_action          =  missing_action
        self.new_categ_action        =  new_categ_action
        self.categ_split_type        =  categ_split_type
        self.coefs                   =  coefs
        self.depth_imp               =  depth_imp
        self.weigh_imp_rows          =  weigh_imp_rows
        self.min_imp_obs             =  min_imp_obs
        self.random_seed             =  random_seed
        self.nthreads                =  nthreads

        self.all_perm                =  bool(all_perm)
        self.recode_categ            =  bool(recode_categ)
        self.coef_by_prop            =  bool(coef_by_prop)
        self.weights_as_sample_prob  =  bool(weights_as_sample_prob)
        self.sample_with_replacement =  bool(sample_with_replacement)
        self.penalize_range          =  bool(penalize_range)
        self.weigh_by_kurtosis       =  bool(weigh_by_kurtosis)
        self.assume_full_distr       =  bool(assume_full_distr)
        self.build_imputer           =  bool(build_imputer)

        self._reset_obj()

    def _reset_obj(self):
        self.cols_numeric_  =  np.array([])
        self.cols_categ_    =  np.array([])
        self._cat_mapping   =  list()
        self._cat_max_lev   =  np.array([])
        self._ncols_numeric =  0
        self._ncols_categ   =  0
        self.is_fitted_     =  False
        self._ntrees        =  0
        self._cpp_obj       =  isoforest_cpp_obj()
        self._is_extended_  =  self.ndim > 1

    def copy(self):
        """
        Get a deep copy of this object

        Returns
        -------
        copied : obj
            A deep copy of this object
        """
        if not self.is_fitted_:
            self._cpp_obj = isoforest_cpp_obj()
            return deepcopy(self)
        else:
            obj_restore = self._cpp_obj
            obj_new = self._cpp_obj.deepcopy()
            try:
                self._cpp_obj = None
                out = deepcopy(self)
            finally:
                self._cpp_obj = obj_restore
            out._cpp_obj = obj_new
            return out

    def get_params(self, deep=True):
        """
        Get parameters for this estimator.

        Kept for compatibility with scikit-learn.

        Parameters
        ----------
        deep : bool
            Ignored.

        Returns
        -------
        params : dict
            Parameter names mapped to their values.
        """
        import inspect
        return {param.name:getattr(self, param.name) for param in inspect.signature(self.__init__).parameters.values()}

    def set_params(self, **params):
        """
        Set the parameters of this estimator.

        Kept for compatibility with scikit-learn.

        Note
        ----
        Setting any parameter other than the number of threads will reset the model
        - that is, if it was fitted to some data, the fitted model will be lost.
        
        Parameters
        ----------
        **params : dict
            Estimator parameters.

        Returns
        -------
        self : estimator instance
            Estimator instance.
        """
        if not (len(params) == 1 and ("nthreads" in params or "n_jobs" in params)):
            self.is_fitted_ = False
        valid_params = self.get_params(deep=False)
        for k,v in params.items():
            if k not in valid_params:
                raise ValueError("Invalid parameter: ", k)
            setattr(self, k, v)
        return self

    def __str__(self):
        msg = ""
        if self._is_extended_:
            msg += "Extended "
        msg += "Isolation Forest model"
        if (self.prob_pick_avg_gain + self.prob_pick_pooled_gain) > 0 or \
            (self.ndim == 1 and (self.prob_split_avg_gain + self.prob_split_pooled_gain) > 0):
            msg += " (using guided splits)"
        msg += "\n"
        if self.ndim > 1:
            msg += "Splitting by %d variables at a time\n" % self.ndim
        if self.is_fitted_:
            msg += "Consisting of %d trees\n" % self._ntrees
            if self._ncols_numeric > 0:
                msg += "Numeric columns: %d\n" % self._ncols_numeric
            if self._ncols_categ:
                msg += "Categorical columns: %d\n" % self._ncols_categ
        return msg

    def __repr__(self):
        return self.__str__()

    def _get_model_obj(self):
        return self._cpp_obj.get_cpp_obj(self._is_extended_)

    def _get_imputer_obj(self):
        return self._cpp_obj.get_imputer()

    def fit(self, X, y = None, sample_weights = None, column_weights = None, categ_cols = None):
        """
        Fit isolation forest model to data

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Data to which to fit the model. Can pass a NumPy array, Pandas DataFrame, or SciPy sparse CSC matrix.
            If passing a DataFrame, will assume that columns are:
            `Numeric`:
                If their dtype is a subtype of NumPy's 'number' or 'datetime64'.
            `Categorical`:
                If their dtype is 'object', 'Categorical', or 'bool'.
            Other dtypes are not supported.
        y : None
            Not used. Kept as argument for compatibility with SciKit-learn pipelining.
        sample_weights : None or array(n_samples,)
            Sample observation weights for each row of 'X', with higher weights indicating either higher sampling
            probability (i.e. the observation has a larger effect on the fitted model, if using sub-samples), or
            distribution density (i.e. if the weight is two, it has the same effect of including the same data
            point twice), according to parameter 'weights_as_sample_prob' in the model constructor method.
        column_weights : None or array(n_features,)
            Sampling weights for each column in 'X'. Ignored when picking columns by deterministic criterion.
            If passing None, each column will have a uniform weight. Cannot be used when weighting by kurtosis.
        categ_cols : None or array-like
            Columns that hold categorical features, when the data is passed as an array or matrix.
            Categorical columns should contain only integer values with a continuous numeration starting at zero,
            with negative values and NaN taken as missing,
            and the array or list passed here should correspond to the column numbers, with numeration starting
            at zero.
            This might be passed either at construction time or when calling ``fit`` or variations of ``fit``.
            
            This is ignored when the input is passed as a ``DataFrame`` as then it will consider columns as
            categorical depending on their dtype.

        Returns
        -------
        self : obj
            This object.
        """
        self._init(categ_cols)
        if (self.sample_size is None) and (sample_weights is not None) and (self.weights_as_sample_prob):
            raise ValueError("Sampling weights are only supported when using sub-samples for each tree.")
        if column_weights is not None and self.weigh_by_kurtosis:
            raise ValueError("Cannot pass column weights when weighting columns by kurtosis.")
        self._reset_obj()
        X_num, X_cat, ncat, sample_weights, column_weights, nrows = self._process_data(X, sample_weights, column_weights)

        if self.sample_size is None:
            sample_size = nrows
        elif self.sample_size < 1:
            sample_size = int(np.ceil(self.sample_size * nrows))
            if sample_size == 1:
                raise ValueError("Sampling proportion amounts to a single row.")
        else:
            sample_size = self.sample_size
        if self.max_depth == "auto":
            max_depth = 0
            limit_depth = True
        elif self.max_depth is None:
            max_depth = nrows - 1
            limit_depth = False
        else:
            max_depth = self.max_depth
            limit_depth = False

        if self.ncols_per_tree is None:
            ncols_per_tree = 0
        elif self.ncols_per_tree < 1:
            ncols_tot = 0
            if X_num is not None:
                ncols_tot += X_num.shape[1]
            if X_cat is not None:
                ncols_tot += X_cat.shape[1]
            ncols_per_tree = int(np.ceil(self.ncols_per_tree * ncols_tot))
        else:
            ncols_per_tree = self.ncols_per_tree

        if isinstance(self.random_state, np.random.RandomState):
            seed = self.random_state.randint(np.iinfo(np.int32).max)
        else:
            seed = self.random_seed

        self._cpp_obj.fit_model(_get_num_dtype(X_num, sample_weights, column_weights),
                                _get_int_dtype(X_num),
                                X_num, X_cat, ncat, sample_weights, column_weights,
                                ctypes.c_size_t(nrows).value,
                                ctypes.c_size_t(self._ncols_numeric).value,
                                ctypes.c_size_t(self._ncols_categ).value,
                                ctypes.c_size_t(self.ndim).value,
                                ctypes.c_size_t(self.ntry).value,
                                self.coefs,
                                ctypes.c_bool(self.coef_by_prop).value,
                                ctypes.c_bool(self.sample_with_replacement).value,
                                ctypes.c_bool(self.weights_as_sample_prob).value,
                                ctypes.c_size_t(sample_size).value,
                                ctypes.c_size_t(self.ntrees).value,
                                ctypes.c_size_t(max_depth).value,
                                ctypes.c_size_t(ncols_per_tree).value,
                                ctypes.c_bool(limit_depth).value,
                                ctypes.c_bool(self.penalize_range).value,
                                ctypes.c_bool(False).value,
                                ctypes.c_bool(False).value,
                                ctypes.c_bool(False).value,
                                ctypes.c_bool(False).value,
                                ctypes.c_bool(False).value,
                                ctypes.c_bool(self.weigh_by_kurtosis).value,
                                ctypes.c_double(self.prob_pick_avg_gain).value,
                                ctypes.c_double(self.prob_split_avg_gain).value,
                                ctypes.c_double(self.prob_pick_pooled_gain).value,
                                ctypes.c_double(self.prob_split_pooled_gain).value,
                                ctypes.c_double(self.min_gain).value,
                                self.missing_action,
                                self.categ_split_type,
                                self.new_categ_action,
                                ctypes.c_bool(self.build_imputer).value,
                                ctypes.c_size_t(self.min_imp_obs).value,
                                self.depth_imp,
                                self.weigh_imp_rows,
                                ctypes.c_bool(self.build_imputer).value,
                                ctypes.c_bool(False).value,
                                ctypes.c_uint64(seed).value,
                                ctypes.c_int(self.nthreads).value)
        self.is_fitted_ = True
        self._ntrees = self.ntrees
        return self

    def fit_predict(self, X, column_weights = None, output_outlierness = "score",
                    output_distance = None, square_mat = False, output_imputed = False,
                    categ_cols = None):
        """
        Fit the model in-place and produce isolation or separation depths along the way
        
        See the documentation of other methods ('init', 'fit', 'predict', 'predict_distance')
        for details.

        Note
        ----
        The data must NOT contain any duplicate rows.

        Note
        ----
        This function will be faster at predicting average depths than calling 'fit' + 'predict'
        separately when using full row samples.

        Note
        ----
        If using 'penalize_range' = 'True', the resulting scores/depths from this function might differ a bit
        from those of 'fit' + 'predict' ran separately.

        Note
        ----
        Sample weights are not supported for this method.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Data to which to fit the model. Can pass a NumPy array, Pandas DataFrame, or SciPy sparse CSC matrix.
            If passing a DataFrame, will assume that columns are:
            `Numeric`:
                If their dtype is a subtype of NumPy's 'number' or 'datetime64'.
            `Categorical`:
                If their dtype is 'object', 'Categorical', or 'bool'.
            Other dtypes are not supported.
        column_weights : None or array(n_features,)
            Sampling weights for each column in 'X'. Ignored when picking columns by deterministic criterion.
            If passing None, each column will have a uniform weight. Cannot be used when weighting by kurtosis.
            Note that, if passing a DataFrame with both numeric and categorical columns, the column names must
            not be repeated, otherwise the column weights passed here will not end up matching.
        output_outlierness : None or str in ["score", "avg_depth"]
            Desired type of outlierness output. If passing "score", will output standardized outlier score.
            If passing "avg_depth" will output average isolation depth without standardizing.
            If passing 'None', will skip outlierness calculations.
        output_distance : None or str in ["dist", "avg_sep"]
            Type of distance output to produce. If passing "dist", will standardize the average separation
            depths. If passing "avg_sep", will output the average separation depth without standardizing it
            (note that lower separation depth means furthest distance). If passing 'None', will skip distance calculations.
        square_mat : bool
            Whether to produce a full square matrix with the distances. If passing 'False', will output
            only the upper triangular part as a 1-d array in which entry (i,j) with 0 <= i < j < n is located at
            position p(i,j) = (i * (n - (i+1)/2) + j - i - 1). Ignored when passing 'output_distance' = 'None'.
        output_imputed : bool
            Whether to output the data with imputed missing values. Model object must have been initialized
            with 'build_imputer' = 'True'.
        categ_cols : None or array-like
            Columns that hold categorical features, when the data is passed as an array or matrix.
            Categorical columns should contain only integer values with a continuous numeration starting at zero,
            with negative values and NaN taken as missing,
            and the array or list passed here should correspond to the column numbers, with numeration starting
            at zero.
            This might be passed either at construction time or when calling ``fit`` or variations of ``fit``.
            
            This is ignored when the input is passed as a ``DataFrame`` as then it will consider columns as
            categorical depending on their dtype.

        Returns
        -------
        output : array(n_samples,), or dict
            Requested outputs about isolation depth (outlierness), pairwise separation depth (distance), and/or
            imputed missing values. If passing either 'output_distance' or 'output_imputed', will return a dictionary
            with keys "pred" (array(n_samples,)), "dist" (array(n_samples * (n_samples - 1) / 2,) or array(n_samples, n_samples)),
            "imputed" (array-like(n_samples, n_columns)), according to whether each output type is present.
        """
        self._init(categ_cols)
        if self.sample_size is not None:
            raise ValueError("Cannot use 'fit_predict' when the sample size is limited.")
        if self.sample_with_replacement:
            raise ValueError("Cannot use 'fit_predict' or 'fit_transform' when sampling with replacement.")
        if column_weights is not None and self.weigh_by_kurtosis:
            raise ValueError("Cannot pass column weights when weighting columns by kurtosis.")

        if (output_outlierness is None) and (output_distance is None):
            raise ValueError("Must pass at least one of 'output_outlierness' or 'output_distance'.")

        if output_outlierness is not None:
            assert output_outlierness in ["score", "avg_depth"]

        if output_distance is not None:
            assert output_distance in ["dist", "avg_sep"]

        if output_imputed:
            if self.missing_action == "fail":
                raise ValueError("Cannot impute missing values when using 'missing_action' = 'fail'.")
            if not self.build_imputer:
                msg  = "Trying to impute missing values from object "
                msg += "that was initialized with 'build_imputer' = 'False' "
                msg += "- will force 'build_imputer' to 'True'."
                warnings.warn(msg)
                self.build_imputer = True

        self._reset_obj()
        X_num, X_cat, ncat, sample_weights, column_weights, nrows = self._process_data(X, None, column_weights)

        if (output_imputed) and (issparse(X_num)):
            msg  = "Imputing missing values from CSC matrix on-the-fly can be very slow, "
            msg += "it's recommended if possible to fit the model first and then pass the "
            msg += "same matrix as CSR to 'transform'."
            warnings.warn(msg)

        if self.max_depth == "auto":
            max_depth = 0
            limit_depth = True
        elif self.max_depth is None:
            max_depth = nrows - 1
        else:
            max_depth = self.max_depth
            limit_depth = False

        if self.ncols_per_tree is None:
            ncols_per_tree = 0
        elif self.ncols_per_tree < 1:
            ncols_tot = 0
            if X_num is not None:
                ncols_tot += X_num.shape[1]
            if X_cat is not None:
                ncols_tot += X_cat.shape[1]
            ncols_per_tree = int(np.ceil(self.ncols_per_tree * ncols_tot))
        else:
            ncols_per_tree = self.ncols_per_tree

        if isinstance(self.random_state, np.random.RandomState):
            seed = self.random_state.randint(np.iinfo(np.int32).max)
        else:
            seed = self.random_seed

        depths, tmat, dmat, X_num, X_cat = self._cpp_obj.fit_model(_get_num_dtype(X_num, None, column_weights),
                                                                   _get_int_dtype(X_num),
                                                                   X_num, X_cat, ncat, None, column_weights,
                                                                   ctypes.c_size_t(nrows).value,
                                                                   ctypes.c_size_t(self._ncols_numeric).value,
                                                                   ctypes.c_size_t(self._ncols_categ).value,
                                                                   ctypes.c_size_t(self.ndim).value,
                                                                   ctypes.c_size_t(self.ntry).value,
                                                                   self.coefs,
                                                                   ctypes.c_bool(self.coef_by_prop).value,
                                                                   ctypes.c_bool(self.sample_with_replacement).value,
                                                                   ctypes.c_bool(self.weights_as_sample_prob).value,
                                                                   ctypes.c_size_t(nrows).value,
                                                                   ctypes.c_size_t(self.ntrees).value,
                                                                   ctypes.c_size_t(max_depth).value,
                                                                   ctypes.c_size_t(ncols_per_tree).value,
                                                                   ctypes.c_bool(limit_depth).value,
                                                                   ctypes.c_bool(self.penalize_range).value,
                                                                   ctypes.c_bool(output_distance is not None).value,
                                                                   ctypes.c_bool(output_distance == "dist").value,
                                                                   ctypes.c_bool(square_mat).value,
                                                                   ctypes.c_bool(output_outlierness is not None).value,
                                                                   ctypes.c_bool(output_outlierness == "score").value,
                                                                   ctypes.c_bool(self.weigh_by_kurtosis).value,
                                                                   ctypes.c_double(self.prob_pick_avg_gain).value,
                                                                   ctypes.c_double(self.prob_split_avg_gain).value,
                                                                   ctypes.c_double(self.prob_pick_pooled_gain).value,
                                                                   ctypes.c_double(self.prob_split_pooled_gain).value,
                                                                   ctypes.c_double(self.min_gain).value,
                                                                   self.missing_action,
                                                                   self.categ_split_type,
                                                                   self.new_categ_action,
                                                                   ctypes.c_bool(self.build_imputer).value,
                                                                   ctypes.c_size_t(self.min_imp_obs).value,
                                                                   self.depth_imp,
                                                                   self.weigh_imp_rows,
                                                                   ctypes.c_bool(output_imputed).value,
                                                                   ctypes.c_bool(self.all_perm).value,
                                                                   ctypes.c_uint64(seed).value,
                                                                   ctypes.c_int(self.nthreads).value)
        self.is_fitted_ = True
        self._ntrees = self.ntrees

        if (not output_distance) and (not output_imputed):
            return depths
        else:
            outp = {"pred" : depths}
            if output_distance:
                if square_mat:
                    outp["dist"] = dmat
                else:
                    outp["dist"] = tmat
            if output_imputed:
                outp["imputed"] = self._rearrange_imputed(X, X_num, X_cat)
            return outp

    def _process_data(self, X, sample_weights, column_weights):
        ### TODO: this needs a refactoring after introducing 'categ_cols'

        if X.__class__.__name__ == "DataFrame":

            if self.categ_cols is not None:
                warnings.warn("'categ_cols' is ignored when passing a DataFrame as input.")
                self.categ_cols = None

            ### https://stackoverflow.com/questions/25039626/how-do-i-find-numeric-columns-in-pandas
            X_num = X.select_dtypes(include = [np.number, np.datetime64]).to_numpy()
            if X_num.dtype not in [ctypes.c_double, ctypes.c_float]:
                X_num = X_num.astype(ctypes.c_double)
            if not _is_col_major(X_num):
                X_num = np.asfortranarray(X_num)
            X_cat = X.select_dtypes(include = [pd.CategoricalDtype, "object", "bool"]).copy()
            if (X_num.shape[1] + X_cat.shape[1]) == 0:
                raise ValueError("Input data has no columns of numeric or categorical type.")
            elif (X_num.shape[1] + X_cat.shape[1]) < X.shape[1]:
                cols_num = np.array(X.select_dtypes(include = [np.number, np.datetime64]).columns.values)
                cols_cat = np.array(X_cat.columns.values)
                msg  = "Only numeric and categorical columns are supported."
                msg += " Got passed the following types: ["
                msg += ", ".join([str(X[cl].dtype) for cl in X.columns.values if cl not in cols_num and cl not in cols_cat][:3])
                msg += "]\n(Sample problem columns: ["
                msg += ", ".join([str(cl) for cl in X.columns.values if cl not in cols_num and cl not in cols_cat][:3])
                msg += "])"
                raise ValueError(msg)

            self._ncols_numeric = X_num.shape[1]
            self._ncols_categ   = X_cat.shape[1]
            self.cols_numeric_  = np.array(X.select_dtypes(include = [np.number, np.datetime64]).columns.values)
            self.cols_categ_    = np.array(X.select_dtypes(include = [pd.CategoricalDtype, "object", "bool"]).columns.values)
            if not self._ncols_numeric:
                X_num = None
            else:
                nrows = X_num.shape[0]

            if not self._ncols_categ:
                X_cat = None
            else:
                nrows = X_cat.shape[0]

            has_ordered = False
            if X_cat is not None:
                self._cat_mapping = [None for cl in range(X_cat.shape[1])]
                for cl in range(X_cat.shape[1]):
                    if (X_cat[X_cat.columns[cl]].dtype.name == "category") and (X_cat[X_cat.columns[cl]].dtype.ordered):
                        has_ordered = True
                    if (not self.recode_categ) and (X_cat[X_cat.columns[cl]].dtype.name == "category"):
                        self._cat_mapping[cl] = np.array(X_cat[X_cat.columns[cl]].cat.categories)
                        X_cat[X_cat.columns[cl]] = X_cat[X_cat.columns[cl]].cat.codes
                    else:
                        X_cat[X_cat.columns[cl]], self._cat_mapping[cl] = pd.factorize(X_cat[X_cat.columns[cl]])
                    if (self.all_perm
                        and (self.ndim == 1)
                        and (self.prob_pick_pooled_gain or self.prob_split_pooled_gain)
                    ):
                        if np.math.factorial(self._cat_mapping[cl].shape[0]) > np.iinfo(ctypes.c_size_t).max:
                            msg  = "Number of permutations for categorical variables is larger than "
                            msg += "maximum representable integer. Try using 'all_perm=False'."
                            raise ValueError(msg)
                    # https://github.com/pandas-dev/pandas/issues/30618
                    if self._cat_mapping[cl].__class__.__name__ == "CategoricalIndex":
                        self._cat_mapping[cl] = self._cat_mapping[cl].to_numpy()
                X_cat = X_cat.to_numpy()
                if X_cat.dtype != ctypes.c_int:
                    X_cat = X_cat.astype(ctypes.c_int)
                if not _is_col_major(X_cat):
                    X_cat = np.asfortranarray(X_cat)
                if has_ordered:
                    warnings.warn("Data contains ordered categoricals. These are treated as unordered.")

        else:
            if len(X.shape) != 2:
                raise ValueError("Input data must be two-dimensional.")

            X_cat = None
            if self.categ_cols is not None:
                if np.max(self.categ_cols) >= X.shape[1]:
                    raise ValueError("'categ_cols' contains indices higher than the number of columns in 'X'.")
                self.cols_numeric_ = np.setdiff1d(np.arange(X.shape[1]), self.categ_cols)
                if issparse(X) and not isspmatrix_csc(X):
                    X = csc_matrix(X)
                X_cat = X[:, self.categ_cols]
                X = X[:, self.cols_numeric_]

            if X.shape[1]:
                if issparse(X):
                    avoid_sort = False
                    if not isspmatrix_csc(X):
                        warnings.warn("Sparse matrices are only supported in CSC format, will be converted.")
                        X = csc_matrix(X)
                        avoid_sort = True
                    if X.nnz == 0:
                        raise ValueError("'X' has no non-zero entries")

                    if ((X.indptr.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]) or
                        (X.indices.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]) or
                        (X.indptr.dtype != X.indices.dtype) or
                        (X.data.dtype not in [ctypes.c_double, ctypes.c_float])
                    ):
                        X = X.copy()
                    if X.data.dtype not in [ctypes.c_double, ctypes.c_float]:
                        X.data    = X.data.astype(ctypes.c_double)
                    if (X.indptr.dtype != X.indices.dtype) or (X.indices.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]):
                        X.indices = X.indices.astype(ctypes.c_size_t)
                    if (X.indptr.dtype != X.indices.dtype) or (X.indptr.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]):
                        X.indptr  = X.indptr.astype(ctypes.c_size_t)
                    if not avoid_sort:
                        _sort_csc_indices(X)
                
                else:
                    if (X.__class__.__name__ == "ndarray") and (X.dtype not in [ctypes.c_double, ctypes.c_float]):
                        X = X.astype(ctypes.c_double)
                    if (X.__class__.__name__ != "ndarray") or (not _is_col_major(X)):
                        X = np.asfortranarray(X)
                    if X.dtype not in [ctypes.c_double, ctypes.c_float]:
                        X = X.astype(ctypes.c_double)

            self._ncols_numeric = X.shape[1]
            self._ncols_categ   = 0 if (X_cat is None) else X_cat.shape[1]
            if self.categ_cols is None:
                self.cols_numeric_  = np.array([])
            self.cols_categ_    = np.array([])
            self._cat_mapping   = list()

            if (self._ncols_numeric + self._ncols_categ) == 0:
                raise ValueError("'X' has zero columns.")

            if X.shape[1]:
                X_num = X
                nrows = X_num.shape[0]
            else:
                X_num = None
            
            if X_cat is not None:
                if issparse(X_cat):
                    X_cat = X_cat.toarray()
                if np.any(np.isnan(X_cat)):
                    X_cat = X_cat.copy()
                    X_cat[np.isnan(X_cat)] = -1
                if X_cat.dtype != ctypes.c_int:
                    X_cat = X_cat.astype(ctypes.c_int)
                if not _is_col_major(X_cat):
                    X_cat = np.asfortranarray(X_cat)
                self._cat_max_lev = np.max(X_cat, axis=0)
                if np.any(self._cat_max_lev < 0):
                    warnings.warn("Some categorical columns contain only missing values.")
                nrows = X_cat.shape[0]

        if nrows == 0:
            raise ValueError("Input data has zero rows.")
        elif nrows < 2:
            raise ValueError("Input data must have at least 2 rows.")
        elif self.sample_size is not None:
            if self.sample_size > nrows:
                warnings.warn("Input data has fewer rows than sample_size, will decrease sample_size.")
                self.sample_size = None

        if X_cat is not None:
            if self.categ_cols is None:
                ncat = np.array([self._cat_mapping[cl].shape[0] for cl in range(X_cat.shape[1])], dtype = ctypes.c_int)
            else:
                ncat = self._cat_max_lev + 1
                if ncat.dtype != ctypes.c_int:
                    ncat = ncat.astype(ctypes.c_int)
        else:
            ncat = None

        if sample_weights is not None:
            sample_weights = np.array(sample_weights).reshape(-1)
            if (X_num is not None) and (X_num.dtype != sample_weights.dtype):
                sample_weights = sample_weights.astype(X_num.dtype)
            if sample_weights.dtype not in [ctypes.c_double, ctypes.c_float]:
                sample_weights = sample_weights.astype(ctypes.c_double)
            if sample_weights.shape[0] != nrows:
                raise ValueError("'sample_weights' has different number of rows than 'X'.")

        ncols = 0
        if X_num is not None:
            ncols += X_num.shape[1]
        if X_cat is not None:
            ncols += X_cat.shape[1]

        if column_weights is not None:
            column_weights = np.array(column_weights).reshape(-1)
            if (X_num is not None) and (X_num.dtype != column_weights.dtype):
                column_weights = column_weights.astype(X_num.dtype)
            if column_weights.dtype not in [ctypes.c_double, ctypes.c_float]:
                column_weights = column_weights.astype(ctypes.c_double)
            if ncols != column_weights.shape[0]:
                raise ValueError("'column_weights' has %d entries, but data has %d columns." % (column_weights.shape[0], ncols))
            if (X_num is not None) and (X_cat is not None):
                column_weights = np.r_[column_weights[X.columns.values == self.cols_numeric_],
                                       column_weights[X.columns.values == self.cols_categ_]]

        if (sample_weights is not None) and (column_weights is not None) and (sample_weights.dtype != column_weights.dtype):
            sample_weights = sample_weights.astype(ctypes.c_double)
            column_weights = column_weights.astype(ctypes.c_double)

        if self.ndim > 1:
            if self.ndim > ncols:
                msg  = "Model was meant to take %d variables for each split, but data has %d columns."
                msg += " Will decrease number of splitting variables to match number of columns."
                msg = msg % (self.ndim, ncols)
                warnings.warn(msg)
                self.ndim = ncols
                if self.ndim < 2:
                    self._is_extended_ = False

        X_num = _copy_if_subview(X_num)
        X_cat = _copy_if_subview(X_cat)

        return X_num, X_cat, ncat, sample_weights, column_weights, nrows

    def _process_data_new(self, X, allow_csr = True, allow_csc = True, prefer_row_major = False):
        if X.__class__.__name__ == "DataFrame":
            if ((self.cols_numeric_.shape[0] + self.cols_categ_.shape[0]) > 0) and (self.categ_cols is None):
                if self.categ_cols is None:
                    missing_cols = np.setdiff1d(np.r_[self.cols_numeric_, self.cols_categ_], np.array(X.columns.values))
                    if missing_cols.shape[0] > 0:
                        raise ValueError("Input data is missing %d columns - example: [%s]" % (missing_cols.shape[0], ", ".join(missing_cols[:3])))
                else:
                    if X.shape[1] < (self.cols_numeric_.shape[0] + self.cols_categ_.shape[0]):
                        raise ValueError("Error: expected input with %d columns - got: %d." %
                                         ((self.cols_numeric_.shape[0] + self.cols_categ_.shape[0]), X.shape[1]))

                if self._ncols_numeric > 0:
                    if self.categ_cols is None:
                        X_num = X[self.cols_numeric_].to_numpy()
                    else:
                        X_num = X.iloc[:, self.cols_numeric_].to_numpy()
                    
                    if X_num.dtype not in [ctypes.c_double, ctypes.c_float]:
                        X_num = X_num.astype(ctypes.c_double)
                    if (not prefer_row_major) and (not _is_col_major(X_num)):
                        X_num = np.asfortranarray(X_num)
                    nrows = X_num.shape[0]
                else:
                    X_num = None

                if self._ncols_categ > 0:
                    if self.categ_cols is None:
                        X_cat = X[self.cols_categ_].copy()
                        for cl in range(self._ncols_categ):
                            X_cat[self.cols_categ_[cl]] = pd.Categorical(X_cat[self.cols_categ_[cl]], self._cat_mapping[cl]).codes
                    else:
                        X_cat = X.iloc[:, self.categ_cols]
                    X_cat = X_cat.to_numpy()
                    if X_cat.dtype != ctypes.c_int:
                        X_cat = X_cat.astype(ctypes.c_int)
                    if (not prefer_row_major) and (not _is_col_major(X_cat)):
                        X_cat = np.asfortranarray(X_cat)
                    nrows = X_cat.shape[0]
                else:
                    X_cat = None

            elif self._ncols_categ == 0:
                if X.shape[1] < self._ncols_numeric:
                    raise ValueError("Input has different number of columns than data to which model was fit.")
                X_num = X.to_numpy()
                if X_num.dtype not in [ctypes.c_double, ctypes.c_float]:
                    X_num = X_num.astype(ctypes.c_double)
                if (not prefer_row_major) and (not _is_col_major(X_num)):
                    X_num = np.asfortranarray(X_num)
                X_cat = None
                nrows = X_num.shape[0]
            elif self._ncols_numeric == 0:
                if X.shape[1] < self._ncols_categ:
                    raise ValueError("Input has different number of columns than data to which model was fit.")
                X_cat = X.to_numpy()[:, :self._ncols_categ]
                if X_cat.dtype  != ctypes.c_int:
                    X_cat = X_cat.astype(ctypes.c_int)
                if (not prefer_row_major) and (not _is_col_major(X_cat)):
                    X_cat = np.asfortranarray(X_cat)
                X_num = None
                nrows = X_cat.shape[0]
            else:
                nrows = X.shape[0]
                X_num = X.iloc[:, self.cols_numeric_].to_numpy()
                X_cat = X.iloc[:, self.categ_cols].to_numpy()
                if X_num.dtype not in [ctypes.c_double, ctypes.c_float]:
                    X_num = X_num.astype(ctypes.c_double)
                if (not prefer_row_major) and (not _is_col_major(X_num)):
                    X_num = np.asfortranarray(X_num)
                if X_cat.dtype  != ctypes.c_int:
                    X_cat = X_cat.astype(ctypes.c_int)
                if (not prefer_row_major) and (not _is_col_major(X_cat)):
                    X_cat = np.asfortranarray(X_cat)

            if (X_num is not None) and (X_cat is not None) and (_is_col_major(X_num) != _is_col_major(X_cat)):
                if prefer_row_major:
                    X_num = np.ascontiguousarray(X_num)
                    X_cat = np.ascontiguousarray(X_cat)
                else:
                    X_num = np.asfortranarray(X_num)
                    X_cat = np.asfortranarray(X_cat)

        else:
            if (self._ncols_categ > 0) and (self.categ_cols is None):
                raise ValueError("Model was fit to DataFrame with categorical columns, but new input is a numeric array/matrix.")
            if len(X.shape) != 2:
                raise ValueError("Input data must be two-dimensional.")
            if (self.categ_cols is None) and (X.shape[1] < self._ncols_numeric):
                raise ValueError("Input has different number of columns than data to which model was fit.")
            
            if self.categ_cols is None:
                X_cat = None
            else:
                if issparse(X) and (not isspmatrix_csc(X)) and (not isspmatrix_csr(X)):
                    X = csc_matrix(X)
                X_cat = X[:, self.categ_cols]
                if issparse(X_cat):
                    X_cat = X_cat.toarray()
                X = X[:, self.cols_numeric_]

            X_num = None
            if X.shape[1]:
                if issparse(X):
                    avoid_sort = False
                    if isspmatrix_csr(X) and not allow_csr:
                        warnings.warn("Cannot predict from CSR sparse matrix, will convert to CSC.")
                        X = csc_matrix(X)
                        avoid_sort = True
                    elif isspmatrix_csc(X) and not allow_csc:
                        warnings.warn("Method supports sparse matrices only in CSR format, will convert sparse format.")
                        X = csr_matrix(X)
                        avoid_sort = True
                    elif (not isspmatrix_csc(X)) and (not isspmatrix_csr(X)):
                        msg  = "Sparse matrix inputs only supported as "
                        if allow_csc:
                            msg += "CSC"
                            if allow_csr:
                                msg += " or CSR"
                        else:
                            msg += "CSR"
                        msg += " format, will convert to "
                        if allow_csc:
                            msg += "CSC."
                            warnings.warn(msg)
                            X = csc_matrix(X)
                        else:
                            msg += "CSR."
                            warnings.warn(msg)
                            X = csr_matrix(X)
                        avoid_sort = True

                    if ((X.indptr.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]) or
                        (X.indices.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]) or
                        (X.indptr.dtype != X.indices.dtype) or
                        (X.data.dtype not in [ctypes.c_double, ctypes.c_float])
                    ):
                        X = X.copy()
                    if X.data.dtype not in [ctypes.c_double, ctypes.c_float]:
                        X.data    = X.data.astype(ctypes.c_double)
                    if (X.indptr.dtype != X.indices.dtype) or (X.indices.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]):
                        X.indices = X.indices.astype(ctypes.c_size_t)
                    if (X.indptr.dtype != X.indices.dtype) or (X.indptr.dtype not in [ctypes.c_int, np.int64, ctypes.c_size_t]):
                        X.indptr  = X.indptr.astype(ctypes.c_size_t)
                    if not avoid_sort:
                        _sort_csc_indices(X)
                    X_num = X
                
                else:
                    if X.__class__.__name__ != "ndarray":
                        if prefer_row_major:
                            X = np.array(X)
                        else:
                            X = np.asfortranarray(X)
                    if X.dtype not in [ctypes.c_double, ctypes.c_float]:
                        X = X.astype(ctypes.c_double)
                    if (not prefer_row_major) and (not _is_col_major(X)):
                        X = np.asfortranarray(X)
                    X_num = X
                nrows = X_num.shape[0]

        if X_cat is not None:
            nrows = X_cat.shape[0]
            if np.any(np.isnan(X_cat)):
                X_cat = X_cat.copy()
                X_cat[np.isnan(X_cat)] = -1


            if (self.categ_cols is not None) and np.any(X_cat > self._cat_max_lev.reshape((1,-1))):
                X_cat[X_cat > self._cat_max_lev] = -1
            if X_cat.dtype != ctypes.c_int:
                X_cat = X_cat.astype(ctypes.c_int)
            if (not prefer_row_major) and (not _is_col_major(X_cat)):
                X_cat = np.asfortranarray(X_cat)

        X_num = _copy_if_subview(X_num)
        X_cat = _copy_if_subview(X_cat)

        return X_num, X_cat, nrows

    def _rearrange_imputed(self, orig, X_num, X_cat):
        if orig.__class__.__name__ == "DataFrame":
            ncols_imputed = 0
            if X_num is not None:
                if (self.cols_numeric_ is not None) and (self.cols_numeric_.shape[0]):
                    df_num = pd.DataFrame(X_num, columns = self.cols_numeric_ if (self.categ_cols is None) else orig.columns.values[self.cols_numeric_])
                else:
                    df_num = pd.DataFrame(X_num)
                ncols_imputed += df_num.shape[1]
            if X_cat is not None:
                if self.categ_cols is None:
                    df_cat = pd.DataFrame(X_cat, columns = self.cols_categ_)
                    for cl in range(self.cols_categ_.shape[0]):
                        df_cat[self.cols_categ_[cl]] = pd.Categorical.from_codes(df_cat[self.cols_categ_[cl]], self._cat_mapping[cl])
                else:
                    df_cat = pd.DataFrame(X_cat, columns = orig.columns.values[self.categ_cols])
                ncols_imputed += df_cat.shape[1]
            
            if orig.columns.values.shape[0] != ncols_imputed:
                if self.categ_cols is None:
                    cols_new = np.setdiff1d(orig.columns.values, np.r_[self.cols_numeric_, self.cols_categ_])
                else:
                    cols_new = orig.columns[(self._ncols_numeric + self._ncols_categ):]
                if (X_num is not None) and (X_cat is None):
                    out = pd.concat([df_num, orig[cols_new]], axis = 1)
                elif (X_num is None) and (X_cat is not None):
                    out = pd.concat([df_cat, orig[cols_new]], axis = 1)
                else:
                    out = pd.concat([df_num, df_cat, orig[cols_new]], axis = 1)
                out = out[orig.columns.values]
                return out

            if (X_num is not None) and (X_cat is None):
                return df_num[orig.columns.values]
            elif (X_num is None) and (X_cat is not None):
                return df_cat[orig.columns.values]
            else:
                df = pd.concat([df_num, df_cat], axis = 1)
                df = df[orig.columns.values]
                return df

        else: ### not DataFrame

            if issparse(orig):
                outp = orig.copy()
                if (self.categ_cols is None) and (orig.shape[1] == self._ncols_numeric):
                    outp.data[:] = X_num.data
                elif self.categ_cols is None:
                    if isspmatrix_csr(orig):
                        _reconstruct_csr_sliced(
                            outp.data,
                            outp.indptr,
                            X_num.data if (X_num is not None) else np.empty(0, dtype=outp.data.dtype),
                            X_num.indptr if (X_num is not None) else np.zeros(1, dtype=outp.indptr.dtype),
                            outp.shape[0]
                        )
                    else:
                        outp[:, :self._ncols_numeric] = X_num
                else:
                    if isspmatrix_csr(orig):
                        _reconstruct_csr_with_categ(
                            outp.data,
                            outp.indices,
                            outp.indptr,
                            X_num.data if (X_num is not None) else np.empty(0, dtype=outp.data.dtype),
                            X_num.indices if (X_num is not None) else np.empty(0, dtype=outp.indices.dtype),
                            X_num.indptr if (X_num is not None) else np.zeros(1, dtype=outp.indptr.dtype),
                            X_cat,
                            self.cols_numeric_.astype(ctypes.c_size_t) if (self.cols_numeric_ is not None) else np.empty(0, dtype=ctypes.c_size_t),
                            self.categ_cols.astype(ctypes.c_size_t),
                            outp.shape[0], outp.shape[1],
                             _is_col_major(X_cat),
                        )
                    else:
                        if np.any(X_cat < 0):
                            X_cat = X_cat.astype("float")
                            X_cat[X_cat < 0] = np.nan
                        outp[:, self.categ_cols] = X_cat
                        if X_num is not None:
                            outp[:, self.cols_numeric_] = X_num
                return outp
            
            else:
                if (self.categ_cols is None) and (orig.shape[1] == self._ncols_numeric):
                    return X_num
                elif self.categ_cols is None:
                    outp = orig.copy()
                    outp[:, :self._ncols_numeric] = X_num[:, :self._ncols_numeric]
                else:
                    outp = orig.copy()
                    if np.any(X_cat < 0):
                        X_cat = X_cat.astype("float")
                        X_cat[X_cat < 0] = np.nan
                    outp[:, self.categ_cols] = X_cat
                    if X_num is not None:
                        outp[:, self.cols_numeric_] = X_num[:, :self._ncols_numeric]
                return outp


    def predict(self, X, output = "score"):
        """
        Predict outlierness based on average isolation depth

        Calculates the approximate depth that it takes to isolate an observation according to the
        fitted model splits. Can output either the average depth, or a standardized outlier score
        based on whether it takes more or fewer splits than average to isolate observations. In the
        standardized outlier score metric, values closer to 1 indicate more outlierness, while values
        closer to 0.5 indicate average outlierness, and close to 0 more averageness (harder to isolate).
        
        Note
        ----
        The more threads that are set for the model, the higher the memory requirements will be as each
        thread will allocate an array with one entry per row.
        
        Note
        ----
        In order to save memory when fitting and serializing models, the functionality for outputting
        terminal node number will generate index mappings on the fly for all tree nodes, even if passing only
        1 row, so it's only recommended for batch predictions.

        Note
        ----
        The outlier scores/depth predict functionality is optimized for making predictions on one or a
        few rows at a time - for making large batches of predictions, it might be faster to use the
        'fit_predict' functionality.

        Note
        ----
        If using non-random splits (parameters ``prob_pick_avg_gain``, ``prob_pick_pooled_gain``,
        ``prob_split_avg_gain``, ``prob_split_pooled_gain``) and/or range penalizations
        (which are on by default), the distribution of scores might not be centered around 0.5.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Observations for which to predict outlierness or average isolation depth. Can pass
            a NumPy array, Pandas DataFrame, or SciPy sparse CSC or CSR matrix.

            If 'X' is sparse and one wants to obtain the outlier score or average depth or tree
            numbers, it's highly recommended to pass it in CSC format as it will be much faster
            when the number of trees or rows is large.
        output : str, one of "score", "avg_depth", "tree_num"
            Desired type of output. If passing "score", will output standardized outlier score.
            If passing "avg_depth" will output average isolation depth without standardizing. If
            passing "tree_num", will output the index of the terminal node under each tree in
            the model.

        Returns
        -------
        score : array(n_samples,) or array(n_samples, n_trees)
            Requested output type for each row accoring to parameter 'output' (outlier scores,
            average isolation depth, or terminal node indices).
        """
        assert self.is_fitted_
        assert output in ["score", "avg_depth", "tree_num"]
        X_num, X_cat, nrows = self._process_data_new(X, prefer_row_major = True)
        if output == "tree_num":
            if self.missing_action == "divide":
                raise ValueError("Cannot output tree number when using 'missing_action' = 'divide'.")
            if (self._ncols_categ > 0) and (self.new_categ_action == "weighted"):
                raise ValueError("Cannot output tree number when using 'new_categ_action' = 'weighted'.")
            if nrows == 1:
                warnings.warn("Predicting tree number is slow, not recommended to do for 1 row at a time.")

        depths, tree_num = self._cpp_obj.predict(_get_num_dtype(X_num, None, None), _get_int_dtype(X_num),
                                                 X_num, X_cat, self._is_extended_,
                                                 ctypes.c_size_t(nrows).value,
                                                 ctypes.c_int(self.nthreads).value,
                                                 ctypes.c_bool(output == "score").value,
                                                 ctypes.c_bool(output == "tree_num").value)

        if output in ["score", "avg_depth"]:
            return depths
        else:
            return tree_num

    def decision_function(self, X):
        """
        Wrapper for 'predict' with 'output=score'

        This function is kept for compatibility with SciKit-Learn.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Observations for which to predict outlierness or average isolation depth. Can pass
            a NumPy array, Pandas DataFrame, or SciPy sparse CSC or CSR matrix.

        Returns
        -------
        score : array(n_samples,)
            Outlier scores for the rows in 'X' (the higher, the most anomalous).
        """
        return self.predict(X, output="score")

    def predict_distance(self, X, output = "dist", square_mat = False, X_ref = None):
        """
        Predict approximate distances between points

        Predict approximate pairwise distances between points or individual distances between
        two sets of points based on how many
        splits it takes to separate them. Can output either the average number of paths,
        or a standardized metric (in the same way as the outlier score) in which values closer
        to zero indicate nearer points, closer to one further away points, and closer to 0.5
        average distance.

        Note
        ----
        The more threads that are set for the model, the higher the memory requirement will be as each
        thread will allocate an array with one entry per combination.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Observations for which to calculate approximate pairwise distances,
            or first group for distances between sets of points. Can pass
            a NumPy array, Pandas DataFrame, or SciPy sparse CSC matrix.
        output : str, one of "dist", "avg_sep"
            Type of output to produce. If passing "dist", will standardize the average separation
            depths. If passing "avg_sep", will output the average separation depth without standardizing it
            (note that lower separation depth means furthest distance).
        square_mat : bool
            Whether to produce a full square matrix with the pairwise distances. If passing 'False', will output
            only the upper triangular part as a 1-d array in which entry (i,j) with 0 <= i < j < n is located at
            position p(i,j) = (i * (n - (i+1)/2) + j - i - 1).
            Ignored when passing ``X_ref``.
        X_ref : array or array-like (n_ref, n_features)
            Second group of observations. If passing it, will calculate distances between each point in
            ``X`` and each point in ``X_ref``. If passing ``None`` (the default), will calculate
            pairwise distances between the points in ``X``.
            Must be of the same type as ``X`` (e.g. array, DataFrame, CSC).

        Returns
        -------
        dist : array(n_samples * (n_samples - 1) / 2,) or array(n_samples, n_samples) or array(n_samples, n_ref)
            Approximate distances or average separation depth between points, according to
            parameter 'output'. Shape and size depends on parameter ``square_mat``, or ``X_ref`` if passed.
        """
        assert self.is_fitted_
        if not self._is_extended_:
            if (self._ncols_categ) and (self.new_categ_action == "weighted") and (self.missing_action != "divide"):
                msg  = "Cannot predict distances when using "
                msg += "'new_categ_action' = 'weighted' "
                msg += "if 'missing_action' != 'divide'."
                raise ValueError(msg)
        assert output in ["dist", "avg_sep"]

        if X_ref is None:
            nobs_group1 = 0
        else:
            if X.__class__ != X_ref.__class__:
                raise ValueError("'X' and 'X_ref' must be of the same class.")
            nobs_group1 = X.shape[0]
            if X.__class__.__name__ == "DataFrame":
                X = X.append(X_ref, ignore_index = True)
            elif issparse(X):
                X = sp_vstack([X, X_ref])
            else:
                X = np.vstack([X, X_ref])

        X_num, X_cat, nrows = self._process_data_new(X, allow_csr = False, prefer_row_major = False)
        if nrows == 1:
            raise ValueError("Cannot calculate pairwise distances for only 1 row.")

        tmat, dmat, rmat = self._cpp_obj.dist(_get_num_dtype(X_num, None, None), _get_int_dtype(X_num),
                                              X_num, X_cat, self._is_extended_,
                                              ctypes.c_size_t(nrows).value,
                                              ctypes.c_int(self.nthreads).value,
                                              ctypes.c_bool(self.assume_full_distr).value,
                                              ctypes.c_bool(output == "dist").value,
                                              ctypes.c_bool(square_mat).value,
                                              ctypes.c_size_t(nobs_group1).value)
        
        if X_ref is not None:
            return rmat
        elif square_mat:
            return dmat
        else:
            return tmat

    def transform(self, X):
        """
        Impute missing values in the data using isolation forest model

        Note
        ----
        In order to use this functionality, the model must have been built with imputation capabilities ('build_imputer' = 'True').

        Note
        ----
        Categorical columns, if imputed, will always come out with pandas categorical dtype.

        Note
        ----
        If the input type is a DataFrame and the model itself was also fitted to a DataFrame, the input
        may contain new columns (i.e. not present when the model was fitted),
        which will be output as-is. If it is an array or sparse matrix, should not contain any new columns.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Data for which missing values should be imputed. Can pass a NumPy array, Pandas DataFrame, or SciPy sparse CSR matrix.
            If passing a DataFrame, will assume that columns are categorical if their dtype is 'object', 'Categorical', or 'bool',
            and will assume they are numerical if their dtype is a subtype of NumPy's 'number' or 'datetime64'.
            Other dtypes are not supported.

        Returns
        -------
        X_imputed : array or array-like (n_samples, n_features)
            Object of the same type and dimensions as 'X', but with missing values already imputed. Categorical
            columns will be output as pandas's 'Categorical' regardless of their dtype in 'X'.
        """
        assert self.is_fitted_
        if not self.build_imputer:
            raise ValueError("Cannot impute missing values with model that was built with 'build_imputer' =  'False'.")
        if self.missing_action == "fail":
            raise ValueError("Cannot impute missing values when using 'missing_action' = 'fail'.")

        X_num, X_cat, nrows = self._process_data_new(X, allow_csr = True, allow_csc = False, prefer_row_major = True)
        if X.__class__.__name__ != "DataFrame":
            if X_num is not None:
                if X_num.shape[1] == self._ncols_numeric:
                    X_num = X_num.copy()
                else:
                    X_num = X_num[:, :self._ncols_numeric].copy()
            if X_cat is not None:
                X_cat = X_cat.copy()
        X_num, X_cat = self._cpp_obj.impute(_get_num_dtype(X_num, None, None), _get_int_dtype(X_num),
                                            X_num, X_cat,
                                            ctypes.c_bool(self._is_extended_).value,
                                            ctypes.c_size_t(nrows).value,
                                            ctypes.c_int(self.nthreads).value)
        return self._rearrange_imputed(X, X_num, X_cat)

    def fit_transform(self, X, y = None, column_weights = None, categ_cols = None):
        """
        SciKit-Learn pipeline-compatible version of 'fit_predict'

        Will fit the model and output imputed missing values. Intended to be used as part of SciKit-learn
        pipelining. Note that this is just a wrapper over 'fit_predict' with parameter 'output_imputed' = 'True'.
        See the documentation of 'fit_predict' for details.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Data to which to fit the model and whose missing values need to be imputed. Can pass a NumPy array, Pandas DataFrame,
            or SciPy sparse CSC matrix.
            If passing a DataFrame, will assume that columns are categorical if their dtype is 'object', 'Categorical', or 'bool',
            and will assume they are numerical if their dtype is a subtype of NumPy's 'number' or 'datetime64'.
            Other dtypes are not supported.
        y : None
            Not used.
        column_weights : None or array(n_features,)
            Sampling weights for each column in 'X'. Ignored when picking columns by deterministic criterion.
            If passing None, each column will have a uniform weight. Cannot be used when weighting by kurtosis.
            Note that, if passing a DataFrame with both numeric and categorical columns, the column names must
            not be repeated, otherwise the column weights passed here will not end up matching.
        categ_cols : None or array-like
            Columns that hold categorical features, when the data is passed as an array or matrix.
            Categorical columns should contain only integer values with a continuous numeration starting at zero,
            with negative values and NaN taken as missing,
            and the array or list passed here should correspond to the column numbers, with numeration starting
            at zero.
            This might be passed either at construction time or when calling ``fit`` or variations of ``fit``.
            
            This is ignored when the input is passed as a ``DataFrame`` as then it will consider columns as
            categorical depending on their dtype.

        Returns
        -------
        imputed : array-like(n_samples, n_columns)
            Input data 'X' with missing values imputed according to the model.
        """
        if self.sample_size is None:
            outp = self.fit_predict(X = X, column_weights = column_weights, output_imputed = True)
            return outp["imputed"]
        else:
            self.fit(X = X, column_weights = column_weights)
            return self.transform(X)

    def partial_fit(self, X, sample_weights = None, column_weights = None):
        """
        Add additional (single) tree to isolation forest model

        Adds a single tree fit to the full (non-subsampled) data passed here. Must
        have the same columns as previously-fitted data.

        Parameters
        ----------
        X : array or array-like (n_samples, n_features)
            Data to which to fit the new tree. Can pass a NumPy array, Pandas DataFrame, or SciPy sparse CSC matrix.
            If passing a DataFrame, will assume that columns are categorical if their dtype is 'object', 'Categorical', or 'bool',
            and will assume they are numerical if their dtype is a subtype of NumPy's 'number' or 'datetime64'.
            Other dtypes are not supported.
        sample_weights : None or array(n_samples,)
            Sample observation weights for each row of 'X', with higher weights indicating
            distribution density (i.e. if the weight is two, it has the same effect of including the same data
            point twice). If not 'None', model must have been built with 'weights_as_sample_prob' = 'False'.
        column_weights : None or array(n_features,)
            Sampling weights for each column in 'X'. Ignored when picking columns by deterministic criterion.
            If passing None, each column will have a uniform weight. Cannot be used when weighting by kurtosis.

        Returns
        -------
        self : obj
            This object.
        """
        if not self.is_fitted_:
            self._init()
        if (sample_weights is not None) and (self.weights_as_sample_prob):
            raise ValueError("Cannot use sampling weights with 'partial_fit'.")
        if (column_weights is not None) and (self.weigh_by_kurtosis):
            raise ValueError("Cannot pass column weights when weighting columns by kurtosis.")

        if not self.is_fitted_:
            trees_restore = self.ntrees
            try:
                self.ntrees = 1
                self.fit(X = X, sample_weights = sample_weights, column_weights = column_weights)
            finally:
                self.ntrees = trees_restore
            return self
        
        X_num, X_cat, nrows = self._process_data_new(X, allow_csr = False, prefer_row_major = False)
        if sample_weights is not None:
            sample_weights = np.array(sample_weights).reshape(-1)
            if (X_num is not None) and (X_num.dtype != sample_weights.dtype):
                sample_weights = sample_weights.astype(X_num.dtype)
            if sample_weights.dtype not in [ctypes.c_double, ctypes.c_float]:
                sample_weights = sample_weights.astype(ctypes.c_double)
            assert sample_weights.shape[0] == X.shape[0]
        if column_weights is not None:
            column_weights = np.array(column_weights).reshape(-1)
            if (X_num is not None) and (X_num.dtype != column_weights.dtype):
                column_weights = column_weights.astype(X_num.dtype)
            if column_weights.dtype not in [ctypes.c_double, ctypes.c_float]:
                column_weights = column_weights.astype(ctypes.c_double)
            assert column_weights.shape[0] == X.shape[1]
        if (sample_weights is not None) and (column_weights is not None) and (sample_weights.dtype != column_weights.dtype):
            sample_weights = sample_weights.astype(ctypes.c_double)
            column_weights = column_weights.astype(ctypes.c_double)
        ncat = None
        if self._ncols_categ > 0:
            ncat = np.array([arr.shape[0] for arr in self._cat_mapping]).astype(ctypes.c_int)
        if self.max_depth == "auto":
            max_depth = 0
            limit_depth = True
        elif self.max_depth is None:
            max_depth = nrows - 1
        else:
            max_depth = self.max_depth
            limit_depth = False

        if self.ncols_per_tree is None:
            ncols_per_tree = 0
        elif self.ncols_per_tree < 1:
            ncols_tot = 0
            if X_num is not None:
                ncols_tot += X_num.shape[1]
            if X_cat is not None:
                ncols_tot += X_cat.shape[1]
            ncols_per_tree = int(np.ceil(self.ncols_per_tree * ncols_tot))
        else:
            ncols_per_tree = self.ncols_per_tree

        self._cpp_obj.fit_tree(_get_num_dtype(X_num, sample_weights, column_weights),
                               _get_int_dtype(X_num),
                               X_num, X_cat, ncat, sample_weights, column_weights,
                               ctypes.c_size_t(nrows).value,
                               ctypes.c_size_t(self._ncols_numeric).value,
                               ctypes.c_size_t(self._ncols_categ).value,
                               ctypes.c_size_t(self.ndim).value,
                               ctypes.c_size_t(self.ntry).value,
                               self.coefs,
                               ctypes.c_bool(self.coef_by_prop).value,
                               ctypes.c_size_t(max_depth).value,
                               ctypes.c_size_t(ncols_per_tree).value,
                               ctypes.c_bool(limit_depth).value,
                               ctypes.c_bool(self.penalize_range).value,
                               ctypes.c_bool(self.weigh_by_kurtosis).value,
                               ctypes.c_double(self.prob_pick_avg_gain).value,
                               ctypes.c_double(self.prob_split_avg_gain).value,
                               ctypes.c_double(self.prob_pick_pooled_gain).value,
                               ctypes.c_double(self.prob_split_pooled_gain).value,
                               ctypes.c_double(self.min_gain).value,
                               self.missing_action,
                               self.categ_split_type,
                               self.new_categ_action,
                               ctypes.c_bool(self.build_imputer).value,
                               ctypes.c_size_t(self.min_imp_obs).value,
                               self.depth_imp,
                               self.weigh_imp_rows,
                               ctypes.c_bool(self.all_perm).value,
                               ctypes.c_int(self.nthreads).value)
        self._ntrees += 1
        return self

    def get_num_nodes(self):
        """
        Get number of nodes per tree

        Gets the number of nodes per tree, along with the number of terminal nodes.

        Returns
        -------
        nodes : tuple(array(n_trees,), array(n_trees,))
            A tuple in which the first element denotes the total number of nodes
            in each tree, and the second element denotes the number of terminal
            nodes. Both are returned as arrays having one entry per tree.
        """
        assert self.is_fitted_
        n_nodes, n_terminal = self._cpp_obj.get_n_nodes(ctypes.c_bool(self._is_extended_).value,
                                                        ctypes.c_int(self.nthreads).value)
        return n_nodes, n_terminal

    def append_trees(self, other):
        """
        Appends isolation trees from another Isolation Forest model into this one

        This function is intended for merging models **that use the same hyperparameters** but
        were fitted to different subsets of data.

        In order for this to work, both models must have been fit to data in the same format - 
        that is, same number of columns, same order of the columns, and same column types, although
        not necessarily same object classes (e.g. can mix ``np.array`` and ``scipy.sparse.csc_matrix``).

        If the data has categorical variables, the models should have been built with parameter
        ``recode_categ=False`` in the class constructor (which is **not** the
        default), and the categorical columns passed as type ``pd.Categorical`` with the same encoding -
        otherwise different models might be using different encodings for each categorical column,
        which will not be preserved as only the trees will be appended without any associated metadata.

        Note
        ----
        This function will not perform any checks on the inputs, and passing two incompatible
        models (e.g. fit to different numbers of columns) will result in wrong results and
        potentially crashing the Python process when using it.

        Parameters
        ----------
        other : IsolationForest
            Another Isolation Forest model from which trees will be appended to this model.
            It will not be modified during the call to this function.

        Returns
        -------
        self : obj
            This object.
        """
        assert self.is_fitted_
        assert other.is_fitted_
        assert isinstance(other, IsolationForest)

        if (self._is_extended_) != (other._is_extended_):
            raise ValueError("Cannot mix extended and regular isolation forest models (ndim=1).")

        if self.cols_categ_.shape[0]:
            warnings.warn("Merging models with categorical features might give wrong results.")

        self._cpp_obj.append_trees_from_other(other._cpp_obj, self._is_extended_)
        self._ntrees += other._ntrees

        return self

    def export_model(self, file, use_cpp = True):
        """
        Export Isolation Forest model

        Save Isolation Forest model to a serialized file along with its
        metadata, in order to be re-used in Python or in the R or the C++ versions of this package.
        
        Although the model objects are always serializable through ``pickle``, this function
        might provide a faster alternative and use less memory when the models to serialize are big.
        
        Note that, if the model was fitted to a ``DataFrame``, the column names must be
        something exportable as JSON, and must be something that R could
        use as column names (e.g. strings/character).
        
        It is recommended to visually inspect the produced ``.metadata`` file in any case.

        This function will create 2 files: the serialized model, in binary format,
        with the name passed in ``file``; and a metadata file in JSON format with the same
        name but ending in ``.metadata``. The second file should **NOT** be edited manually,
        except for the field ``nthreads`` if desired.
        
        If the model was built with ``build_imputer=True``, there will also be a third binary file
        ending in ``.imputer``.
        
        The metadata will contain, among other things, the encoding that was used for
        categorical columns - this is under ``data_info.cat_levels``, as an array of arrays by column,
        with the first entry for each column corresponding to category 0, second to category 1,
        and so on (the C++ version takes them as integers). When passing ``categ_cols``, there
        will be no encoding but it will save the maximum category integer and the column
        numbers instead of names.
        
        The serialized file can be used in the C++ version by reading it as a binary raw file
        and de-serializing its contents with the ``cereal`` library or using the provided C++ functions
        for de-serialization. If using ``ndim=1``, it will be an object of class ``IsoForest``, and if
        using ``ndim>1``, will be an object of class ``ExtIsoForest``. The imputer file, if produced, will
        be an object of class ``Imputer``.

        Be aware that this function will write raw bytes from memory as-is without compression,
        so the file sizes can end up being much larger than when using ``pickle``.
        
        The metadata is not used in the C++ version, but is necessary for the R and Python versions.

        Note
        ----
        **Important:** The model treats boolean variables as categorical. Thus, if the model was fit
        to a ``DataFrame`` with boolean columns, when importing this model into C++, they need to be
        encoded in the same order - e.g. the model might encode ``True`` as zero and ``False``
        as one - you need to look at the metadata for this. Also, if using some of Pandas' own
        Boolean types, these might end up as non-boolean categorical, and if importing the model into R,
        you might need to pass values as e.g. ``"True"`` instead of ``TRUE`` (look at the ``.metadata``
        file to determine this).

        Parameters
        ----------
        file : str
            The output file path into which to export the model. Must be a file name, not a
            file handle.
        use_cpp : bool
            Whether to use C++ directly for IO. Using the C++ funcionality directly is faster, and
            will write directly to a file instead of first creating the file contents in-memory,
            but in Windows, if the library was compiled with a compiler other than MSVC,
            file paths that contain non-ASCII characters will faill to write
            and might crash the Python process along with it. If passing ``False``, it will at
            first create the file contents in-memory in a Python object, and then use a Python
            file handle to write such contents into a file.

        Returns
        -------
        self : obj
            This object.

        References
        ----------
        .. [1] https://uscilab.github.io/cereal
        """
        assert self.is_fitted_
        metadata = self._export_metadata()
        with open(file + ".metadata", "w") as of:
            json.dump(metadata, of, indent=4)
        self._cpp_obj.serialize_obj(file, use_cpp, self.ndim > 1, has_imputer=self.build_imputer)
        return self

    @staticmethod
    def import_model(file, use_cpp = False):
        """
        Load an Isolation Forest model exported from R or Python

        Loads a serialized Isolation Forest model as produced and exported
        by the function ``export_model`` or by the R version of this package.
        Note that the metadata must be something
        importable in Python - e.g. column names must be valid for Pandas.
        It's recommended to visually inspect the ``.metadata`` file in any case.
        
        While the model objects can be serialized through ``pickle``, using the
        package's own functions might result in a faster and more memory-efficient
        alternative.

        Note
        ----
        This is a static class method - i.e. should be called like this:
            ``iso = IsolationForest.import_model(...)``
        (i.e. no parentheses after `IsolationForest`)
        
        Parameters
        ----------
        file : str
            The input file path containing an exported model along with its metadata file.
            Must be a file name, not a file handle.
        use_cpp : bool
            Whether to use C++ directly for IO. Using the C++ funcionality directly is faster, and
            will read directly from a file into a model object instead of first reading the file
            contents in-memory, but in Windows, if the library was compiled with a compiler other than MSVC,
            file paths that contain non-ASCII characters will
            faill to read and might crash the Python process along with it. If passing ``False``,
            it will at first read the file contents in-memory into a Python object, and then recreate
            the model from those bytes.

        Returns
        -------
        iso : IsolationForest
            An Isolation Forest model object reconstructed from the serialized file
            and ready to use.
        """
        obj = IsolationForest()
        metadata_file = file + ".metadata"
        with open(metadata_file, "r") as ff:
            metadata = json.load(ff)
        obj._take_metadata(metadata)
        obj._cpp_obj.deserialize_obj(file, obj.ndim > 1, use_cpp)
        return obj

    def generate_sql(self, enclose="doublequotes", output_tree_num = False, tree = None,
                     table_from = None, select_as = "outlier_score",
                     column_names = None, column_names_categ = None):
        """
        Generate SQL statements representing the model prediction function

        Generate SQL statements - either separately per tree (the default),
        for a single tree if needed (if passing ``tree``), or for all trees
        concatenated together (if passing ``table_from``). Can also be made
        to output terminal node numbers (numeration starting at zero).

        Note
        ----
        Making predictions through SQL is much less efficient than from the model
        itself, as each terminal node will have to check all of the conditions
        that lead to it instead of passing observations down a tree.

        Note
        ----
        If constructed with the default arguments, the model will not perform any
        sub-sampling, which can lead to very big trees. If it was fit to a large
        dataset, the generated SQL might consist of gigabytes of text, and might
        lay well beyond the character limit of commands accepted by SQL vendors.

        Note
        ----
        The generated SQL statements will not include range penalizations, thus
        predictions might differ from calls to ``predict`` when using
        ``penalize_range=True``.

        Note
        ----
        The generated SQL statements will only include handling of missing values
        when using ``missing_action="impute"``. When using the single-variable
        model with categorical variables + subset splits, the rule buckets might be
        incomplete due to not including categories that were not present in a given
        node - this last point can be avoided by using ``new_categ_action="smallest"``,
        ``new_categ_action="random"``, or ``missing_action="impute"`` (in the latter
        case will treat them as missing, but the ``predict`` function might treat
        them differently).

        Note
        ----
        The resulting statements will include all the tree conditions as-is,
        with no simplification. Thus, there might be lots of redundant conditions
        in a given terminal node (e.g. "X > 2" and "X > 1", the second of which is
        redundant).

        Parameters
        ----------
        enclose : str
            With which symbols to enclose the column names in the select statement
            so as to make them SQL compatible in case they include characters like dots.
            Options are:

            ``"doublequotes"``:
                Will enclose them as ``"column_name"`` - this will work for e.g. PostgreSQL.

            ``"squarebraces"``:
                Will enclose them as ``[column_name]`` - this will work for e.g. SQL Server.

            ``"none"``:
                Will output the column names as-is (e.g. ``column_name``)
        output_tree_num : bool
            Whether to make the statements return the terminal node number
            instead of the isolation depth. The numeration will start at zero.
        tree : int or None
            Tree for which to generate SQL statements. If passed, will generate
            the statements only for that single tree. If passing 'None', will
            generate statements for all trees in the model.
        table_from : str or None
            If passing this, will generate a single select statement for the
            outlier score from all trees, selecting the data from the table
            name passed here. In this case, will always output the outlier
            score, regardless of what is passed under ``output_tree_num``.
        select_as : str
            Alias to give to the generated outlier score in the select statement.
            Ignored when not passing ``table_from``.
        column_names : None or list[str]
            Column names to use for the **numeric** columns.
            If not passed and the model was fit to a ``DataFrame``, will use the column
            names from that ``DataFrame``, which can be found under ``self.cols_numeric_``.
            If not passing it and the model was fit to data in a format other than
            ``DataFrame``, the columns will be named "column_N" in the resulting
            SQL statement. Note that the names will be taken verbatim - this function will
            not do any checks for whether they constitute valid SQL or not, and will not
            escape characters such as double quotation marks.
        column_names_categ : None or list[str]
            Column names to use for the **categorical** columns.
            If not passed, will use the column names from the ``DataFrame`` to which the
            model was fit. These can be found under ``self.cols_categ_``.

        Returns
        -------
        sql : list[str] or str
            A list of SQL statements for each tree as strings, or the SQL statement
            for a single tree if passing 'tree', or a single select-from SQL statement
            with all the trees concatenated if passing ``table_from``.
        """
        assert self.is_fitted_
        
        single_tree = False
        if tree is not None:
            if isinstance(tree, float):
                tree = int(tree)
            assert isinstance(tree, int)
            assert tree >= 0
            assert tree < self._ntrees
            single_tree = True
        else:
            tree = 0
        output_tree_num = bool(output_tree_num)

        if self._ncols_numeric:
            if column_names is not None:
                if len(column_names) != self._ncols_numeric:
                    raise ValueError("'column_names' must have %d entries." % self._ncols_numeric)
            else:
                if self.cols_numeric_.shape[0]:
                    column_names = self.cols_numeric_
                else:
                    column_names = ["column_" + str(cl) for cl in range(self._ncols_numeric)]
        else:
            column_names = []

        if self.cols_categ_.shape[0]:
            if column_names_categ is not None:
                if len(column_names_categ) != self.cols_categ_.shape[0]:
                    raise ValueError("'column_names_categ' must have %d entries." % self.cols_categ_.shape[0])
            else:
                column_names_categ = self.cols_categ_
            categ_levels = [[str(lev) for lev in mp] for mp in self._cat_mapping]
        else:
            column_names_categ = []
            categ_levels = []

        assert enclose in ["doublequotes", "squarebraces", "none"]
        if enclose != "none":
            enclose_left  = '"' if (enclose == "doublequotes") else '['
            enclose_right = '"' if (enclose == "doublequotes") else ']'
            column_names = [enclose_left + cl + enclose_right for cl in column_names]
            column_names_categ = [enclose_left + cl + enclose_right for cl in column_names_categ]

        out = [s for s in self._cpp_obj.generate_sql(self.ndim > 1,
                                                     column_names, column_names_categ, categ_levels,
                                                     output_tree_num, single_tree, tree, self.nthreads)]
        if single_tree:
            return out[0]
        return out

    def _denumpify_list(self, lst):
        return [int(el) if np.issubdtype(el.__class__, np.int) else el for el in lst]

    def _export_metadata(self):
        if (self.max_depth is not None) and (self.max_depth != "auto"):
            self.max_depth = int(self.max_depth)

        data_info = {
            "ncols_numeric" : int(self._ncols_numeric), ## is in c++
            "ncols_categ" : int(self._ncols_categ),  ## is in c++
            "cols_numeric" : list(self.cols_numeric_),
            "cols_categ" : list(self.cols_categ_),
            "cat_levels" : [list(m) for m in self._cat_mapping],
            "categ_cols" : list(self.categ_cols),
            "categ_max" : list(self._cat_max_lev)
        }

        ### Beaware of np.int64, which looks like a Python integer but is not accepted by json
        data_info["cols_numeric"] = self._denumpify_list(data_info["cols_numeric"])
        data_info["cols_categ"] = self._denumpify_list(data_info["cols_categ"])
        data_info["categ_cols"] = self._denumpify_list(data_info["categ_cols"])
        data_info["categ_max"] = self._denumpify_list(data_info["categ_max"])
        if len(data_info["cat_levels"]):
            data_info["cat_levels"] = [self._denumpify_list(lst) for lst in data_info["cat_levels"]]

        model_info = {
            "ndim" : int(self.ndim),
            "nthreads" : int(self.nthreads),
            "build_imputer" : bool(self.build_imputer)
        }

        params = {
            "sample_size" : self.sample_size,
            "ntrees" : int(self._ntrees),  ## is in c++
            "ntry" : int(self.ntry),
            "max_depth" : self.max_depth,
            "ncols_per_tree" : self.ncols_per_tree,
            "prob_pick_avg_gain" : float(self.prob_pick_avg_gain),
            "prob_pick_pooled_gain" : float(self.prob_pick_pooled_gain),
            "prob_split_avg_gain" : float(self.prob_split_avg_gain),
            "prob_split_pooled_gain" : float(self.prob_split_pooled_gain),
            "min_gain" : float(self.min_gain),
            "missing_action" : self.missing_action,  ## is in c++
            "new_categ_action" : self.new_categ_action,  ## is in c++
            "categ_split_type" : self.categ_split_type,  ## is in c++
            "coefs" : self.coefs,
            "depth_imp" : self.depth_imp,
            "weigh_imp_rows" : self.weigh_imp_rows,
            "min_imp_obs" : int(self.min_imp_obs),
            "random_seed" : self.random_seed,
            "all_perm" : self.all_perm,
            "coef_by_prop" : self.coef_by_prop,
            "weights_as_sample_prob" : self.weights_as_sample_prob,
            "sample_with_replacement" : self.sample_with_replacement,
            "penalize_range" : self.penalize_range,
            "weigh_by_kurtosis" : self.weigh_by_kurtosis,
            "assume_full_distr" : self.assume_full_distr,
        }

        if params["max_depth"] == "auto":
            params["max_depth"] = 0

        return {"data_info" : data_info, "model_info" : model_info, "params" : params}

    def _take_metadata(self, metadata):
        self._ncols_numeric = metadata["data_info"]["ncols_numeric"]
        self._ncols_categ = metadata["data_info"]["ncols_categ"]
        self.cols_numeric_ = np.array(metadata["data_info"]["cols_numeric"])
        self.cols_categ_ = np.array(metadata["data_info"]["cols_categ"])
        self._cat_mapping = [np.array(lst) for lst in metadata["data_info"]["cat_levels"]]
        self.categ_cols = np.array(metadata["data_info"]["categ_cols"]).reshape(-1).astype(int) if len(metadata["data_info"]["categ_cols"]) else None
        self._cat_max_lev = np.array(metadata["data_info"]["categ_max"]).reshape(-1).astype(int) if (self.categ_cols is not None) else None

        self.ndim = metadata["model_info"]["ndim"]
        self.nthreads = metadata["model_info"]["nthreads"]
        self.build_imputer = metadata["model_info"]["build_imputer"]

        self.sample_size = metadata["params"]["sample_size"]
        self.ntrees = metadata["params"]["ntrees"]
        self._ntrees = self.ntrees
        self.ntry = metadata["params"]["ntry"]
        self.max_depth = metadata["params"]["max_depth"]
        self.ncols_per_tree = metadata["params"]["ncols_per_tree"]
        self.prob_pick_avg_gain = metadata["params"]["prob_pick_avg_gain"]
        self.prob_pick_pooled_gain = metadata["params"]["prob_pick_pooled_gain"]
        self.prob_split_avg_gain = metadata["params"]["prob_split_avg_gain"]
        self.prob_split_pooled_gain = metadata["params"]["prob_split_pooled_gain"]
        self.min_gain = metadata["params"]["min_gain"]
        self.missing_action = metadata["params"]["missing_action"]
        self.new_categ_action = metadata["params"]["new_categ_action"]
        self.categ_split_type = metadata["params"]["categ_split_type"]
        self.coefs = metadata["params"]["coefs"]
        self.depth_imp = metadata["params"]["depth_imp"]
        self.weigh_imp_rows = metadata["params"]["weigh_imp_rows"]
        self.min_imp_obs = metadata["params"]["min_imp_obs"]
        self.random_seed = metadata["params"]["random_seed"]
        self.all_perm = metadata["params"]["all_perm"]
        self.coef_by_prop = metadata["params"]["coef_by_prop"]
        self.weights_as_sample_prob = metadata["params"]["weights_as_sample_prob"]
        self.sample_with_replacement = metadata["params"]["sample_with_replacement"]
        self.penalize_range = metadata["params"]["penalize_range"]
        self.weigh_by_kurtosis = metadata["params"]["weigh_by_kurtosis"]
        self.assume_full_distr = metadata["params"]["assume_full_distr"]

        self.is_fitted_ = True
        self._is_extended_ = self.ndim > 1
        return self
