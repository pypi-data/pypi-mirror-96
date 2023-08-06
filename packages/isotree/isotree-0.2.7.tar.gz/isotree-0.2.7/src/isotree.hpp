/*    Isolation forests and variations thereof, with adjustments for incorporation
*     of categorical variables and missing values.
*     Writen for C++11 standard and aimed at being used in R and Python.
*     
*     This library is based on the following works:
*     [1] Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou.
*         "Isolation forest."
*         2008 Eighth IEEE International Conference on Data Mining. IEEE, 2008.
*     [2] Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou.
*         "Isolation-based anomaly detection."
*         ACM Transactions on Knowledge Discovery from Data (TKDD) 6.1 (2012): 3.
*     [3] Hariri, Sahand, Matias Carrasco Kind, and Robert J. Brunner.
*         "Extended Isolation Forest."
*         arXiv preprint arXiv:1811.02141 (2018).
*     [4] Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou.
*         "On detecting clustered anomalies using SCiForest."
*         Joint European Conference on Machine Learning and Knowledge Discovery in Databases. Springer, Berlin, Heidelberg, 2010.
*     [5] https://sourceforge.net/projects/iforest/
*     [6] https://math.stackexchange.com/questions/3388518/expected-number-of-paths-required-to-separate-elements-in-a-binary-tree
*     [7] Quinlan, J. Ross. C4. 5: programs for machine learning. Elsevier, 2014.
*     [8] Cortes, David. "Distance approximation using Isolation Forests." arXiv preprint arXiv:1910.12362 (2019).
*     [9] Cortes, David. "Imputing missing values with unsupervised random trees." arXiv preprint arXiv:1911.06646 (2019).
* 
*     BSD 2-Clause License
*     Copyright (c) 2019-2021, David Cortes
*     All rights reserved.
*     Redistribution and use in source and binary forms, with or without
*     modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright notice, this
*       list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright notice,
*       this list of conditions and the following disclaimer in the documentation
*       and/or other materials provided with the distribution.
*     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
*     AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
*     IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
*     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
*     FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
*     DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
*     SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
*     CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
*     OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
*     OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef ISOTREE_H
#define ISOTREE_H

/* Standard headers */
#include <stddef.h>
#include <math.h>
#include <limits.h>
#include <string.h>
#include <vector>
#include <iterator>
#include <numeric>
#include <algorithm>
#include <random>
#include <unordered_set>
#include <unordered_map>
#include <memory>
#include <utility>
#include <cstdint>
#include <iostream>
#ifndef _FOR_R
    #include <stdio.h> 
#else
    extern "C" {
        #include <R_ext/Print.h>
    }
    #define printf Rprintf
    #define fprintf(f, message) REprintf(message)
#endif
#ifdef _OPENMP
    #include <omp.h>
#endif
#ifdef _ENABLE_CEREAL
    #include <cereal/archives/binary.hpp>
    #include <cereal/types/vector.hpp>
    #include <sstream>
    #include <string>
    #include <fstream>
#endif
#ifdef _FOR_R
    #include <Rcpp.h>
#endif
#include <signal.h>
typedef void (*sig_t_)(int);


/* By default, will use Mersenne-Twister for RNG, but can be switched to something faster */
#ifdef _USE_MERSENNE_TWISTER
    #if SIZE_MAX >= UINT64_MAX /* 64-bit systems or higher */
        #define RNG_engine std::mt19937_64
    #else /* 32-bit systems and non-standard architectures */
        #define RNG_engine std::mt19937
    #endif
#else
    #define RNG_engine std::default_random_engine
#endif

/* Some operations here are done with bit-shifting and might not work
   correctly on non-standard platforms */
/* TODO: use the built-in enum from C++20 once compilers implement it  */
#if defined(__LITTLE_ENDIAN) && defined(__BYTE_ORDER)
    #define IS_LITTLE_ENDIAN (__BYTE_ORDER == __LITTLE_ENDIAN)
#else
    constexpr static const int ONE = 1;
    #define IS_LITTLE_ENDIAN ((*((unsigned char*)&ONE)) > 0)
#endif

/* Short functions */
#define ix_parent(ix) (((ix) - 1) / 2)  /* integer division takes care of deciding left-right */
#define ix_child(ix)  (2 * (ix) + 1)
/* https://stackoverflow.com/questions/101439/the-most-efficient-way-to-implement-an-integer-based-power-function-powint-int */
#if defined(__LITTLE_ENDIAN) && defined(__BYTE_ORDER) && (__BYTE_ORDER == __LITTLE_ENDIAN)
    #define pow2(n) ( ((size_t) 1) << (n) )
#else
    #define pow2(n) ((size_t)powl((long double)2, (long double)n))
#endif
#define square(x) ((x) * (x))
/* https://stackoverflow.com/questions/2249731/how-do-i-get-bit-by-bit-data-from-an-integer-value-in-c */
#define extract_bit(number, bit) (((number) >> (bit)) & 1)
#ifndef isinf
    #define isinf std::isinf
#endif
#ifndef isnan
    #define isnan std::isnan
#endif
#define is_na_or_inf(x) (isnan(x) || isinf(x))


/* Aliasing for compiler optimizations */
#if defined(__GNUG__) || defined(__GNUC__) || defined(_MSC_VER) || defined(__clang__) || defined(__INTEL_COMPILER)
    #define restrict __restrict
#else
    #define restrict 
#endif

/* MSVC is stuck with an OpenMP version that's 19 years old at the time of writing and does not support unsigned iterators */
#ifdef _OPENMP
    #if (_OPENMP < 200801) || defined(_WIN32) || defined(_WIN64) /* OpenMP < 3.0 */
        #define size_t_for long long
    #else
        #define size_t_for size_t
    #endif
#else
    #define size_t_for size_t
#endif


/*   Apple at some point decided to drop OMP library and headers from its compiler distribution
*    and to alias 'gcc' to 'clang', which work differently when given flags they cannot interpret,
*    causing installation issues with pretty much all scientific software due to OMP headers that
*    would normally do nothing. This piece of code is to allow compilation without OMP header. */
#ifndef _OPENMP
    #define omp_get_thread_num() 0
#endif

/* Some aggregation functions will prefer more precise data types when the data is large */
#define THRESHOLD_LONG_DOUBLE (size_t)1e6

/* Types used through the package */
typedef enum  NewCategAction {Weighted, Smallest, Random}      NewCategAction; /* Weighted means Impute in the extended model */
typedef enum  MissingAction  {Divide,   Impute,   Fail}        MissingAction;  /* Divide is only for non-extended model */
typedef enum  ColType        {Numeric,  Categorical, NotUsed}  ColType;
typedef enum  CategSplit     {SubSet,   SingleCateg}           CategSplit;
typedef enum  GainCriterion  {Averaged, Pooled,   NoCrit}      Criterion;      /* For guided splits */
typedef enum  CoefType       {Uniform,  Normal}                CoefType;       /* For extended model */
typedef enum  UseDepthImp    {Lower,    Higher,   Same}        UseDepthImp;    /* For NA imputation */
typedef enum  WeighImpRows   {Inverse,  Prop,     Flat}        WeighImpRows;   /* For NA imputation */

/* Notes about new categorical action:
*  - For single-variable case, if using 'Smallest', can then pass data at prediction time
*    having categories that were never in the training data (as an integer higher than 'ncat'
*    for that column), but if using 'Random' or 'Weighted', these must be passed as NA (int < 0)
*  - For extended case, 'Weighted' becomes a weighted imputation instead, and if using either
*    'Weighted' or 'Smallest', can pass newer, unseen categories at prediction time too.
*  - If using 'Random', cannot pass new categories at prediction time.
*  - If using 'Weighted' for single-variable case, cannot predict similarity with a value
*    for MissingAction other than 'Divide'. */


/* Structs that are output (modified) from the main function */
typedef struct IsoTree {
    ColType  col_type = NotUsed; /* issues with uninitialized values passed to Cereal */
    size_t   col_num;
    double   num_split;
    std::vector<char> cat_split;
    int      chosen_cat;
    size_t   tree_left;
    size_t   tree_right;
    double   pct_tree_left;
    double   score;        /* will not be integer when there are weights or early stop */
    double   range_low  = -HUGE_VAL;
    double   range_high =  HUGE_VAL;
    double   remainder; /* only used for distance/similarity */

    #ifdef _ENABLE_CEREAL
    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(
            this->col_type,
            this->col_num,
            this->num_split,
            this->cat_split,
            this->chosen_cat,
            this->tree_left,
            this->tree_right,
            this->pct_tree_left,
            this->score,
            this->range_low,
            this->range_high,
            this->remainder
            );
    }
    #endif

    IsoTree() = default;

} IsoTree;

typedef struct IsoHPlane {
    std::vector<size_t>   col_num;
    std::vector<ColType>  col_type;
    std::vector<double>   coef;
    std::vector<double>   mean;
    std::vector<std::vector<double>> cat_coef;
    std::vector<int>      chosen_cat;
    std::vector<double>   fill_val;
    std::vector<double>   fill_new; /* <- when using single categ, coef will be here */

    double   split_point;
    size_t   hplane_left;
    size_t   hplane_right;
    double   score;        /* will not be integer when there are weights or early stop */
    double   range_low  = -HUGE_VAL;
    double   range_high =  HUGE_VAL;
    double   remainder; /* only used for distance/similarity */

    #ifdef _ENABLE_CEREAL
    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(
            this->col_num,
            this->col_type,
            this->coef,
            this->mean,
            this->cat_coef,
            this->chosen_cat,
            this->fill_val,
            this->fill_new,
            this->split_point,
            this->hplane_left,
            this->hplane_right,
            this->score,
            this->range_low,
            this->range_high,
            this->remainder
            );
    }
    #endif

    IsoHPlane() = default;
} IsoHPlane;

/* Note: don't use long doubles in the outside outputs or there will be issues with MINGW in windows */


typedef struct IsoForest {
    std::vector< std::vector<IsoTree> > trees;
    NewCategAction    new_cat_action;
    CategSplit        cat_split_type;
    MissingAction     missing_action;
    double            exp_avg_depth;
    double            exp_avg_sep;
    size_t            orig_sample_size;

    #ifdef _ENABLE_CEREAL
    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(
            this->trees,
            this->new_cat_action,
            this->cat_split_type,
            this->missing_action,
            this->exp_avg_depth,
            this->exp_avg_sep,
            this->orig_sample_size
            );
    }
    #endif

    IsoForest() = default;
} IsoForest;

typedef struct ExtIsoForest {
    std::vector< std::vector<IsoHPlane> > hplanes;
    NewCategAction    new_cat_action;
    CategSplit        cat_split_type;
    MissingAction     missing_action;
    double            exp_avg_depth;
    double            exp_avg_sep;
    size_t            orig_sample_size;

    #ifdef _ENABLE_CEREAL
    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(
            this->hplanes,
            this->new_cat_action,
            this->cat_split_type,
            this->missing_action,
            this->exp_avg_depth,
            this->exp_avg_sep,
            this->orig_sample_size
            );
    }
    #endif

    ExtIsoForest() = default;
} ExtIsoForest;

typedef struct ImputeNode {
    std::vector<double>  num_sum;
    std::vector<double>  num_weight;
    std::vector<std::vector<double>>  cat_sum;
    std::vector<double>  cat_weight;
    size_t               parent;

    #ifdef _ENABLE_CEREAL
    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(
            this->num_sum,
            this->num_weight,
            this->cat_sum,
            this->cat_weight,
            this->parent
            );
    }
    #endif
    ImputeNode() = default;

    ImputeNode(size_t parent)
    {
        this->parent = parent;
    }

} ImputeNode; /* this is for each tree node */

typedef struct Imputer {
    size_t               ncols_numeric;
    size_t               ncols_categ;
    std::vector<int>     ncat;
    std::vector<std::vector<ImputeNode>> imputer_tree;
    std::vector<double>  col_means;
    std::vector<int>     col_modes;

    #ifdef _ENABLE_CEREAL
    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(
            this->ncols_numeric,
            this->ncols_categ,
            this->ncat,
            this->imputer_tree,
            this->col_means,
            this->col_modes
            );
    }
    #endif

    Imputer() = default;

} Imputer;


/* Structs that are only used internally */
template <class real_t, class sparse_ix>
struct InputData {
    real_t*     numeric_data;
    size_t      ncols_numeric;
    int*        categ_data;
    int*        ncat;
    int         max_categ;
    size_t      ncols_categ;
    size_t      nrows;
    size_t      ncols_tot;
    real_t*     sample_weights;
    bool        weight_as_sample;
    real_t*     col_weights;
    real_t*     Xc;           /* only for sparse matrices */
    sparse_ix*  Xc_ind;       /* only for sparse matrices */
    sparse_ix*  Xc_indptr;    /* only for sparse matrices */
    size_t      log2_n;       /* only when using weights for sampling */
    size_t      btree_offset; /* only when using weights for sampling */
    std::vector<double> btree_weights_init;  /* only when using weights for sampling */
    std::vector<char>   has_missing;         /* only used when producing missing imputations on-the-fly */
    size_t              n_missing;           /* only used when producing missing imputations on-the-fly */
};


template <class real_t, class sparse_ix>
struct PredictionData {
    real_t*     numeric_data;
    int*        categ_data;
    size_t      nrows;
    bool        is_col_major;
    size_t      ncols_numeric; /* only required for row-major data */
    size_t      ncols_categ;   /* only required for row-major data */
    real_t*     Xc;            /* only for sparse matrices */
    sparse_ix*  Xc_ind;        /* only for sparse matrices */
    sparse_ix*  Xc_indptr;     /* only for sparse matrices */
    real_t*     Xr;            /* only for sparse matrices */
    sparse_ix*  Xr_ind;        /* only for sparse matrices */
    sparse_ix*  Xr_indptr;     /* only for sparse matrices */
};

typedef struct {
    bool      with_replacement;
    size_t    sample_size;
    size_t    ntrees;
    size_t    ncols_per_tree;
    size_t    max_depth;
    bool      penalize_range;
    uint64_t  random_seed;
    bool      weigh_by_kurt;
    double    prob_pick_by_gain_avg;
    double    prob_split_by_gain_avg;
    double    prob_pick_by_gain_pl;
    double    prob_split_by_gain_pl;
    double    min_gain;
    CategSplit      cat_split_type;
    NewCategAction  new_cat_action;
    MissingAction   missing_action;
    bool            all_perm;

    size_t ndim;        /* only for extended model */
    size_t ntry;        /* only for extended model */
    CoefType coef_type; /* only for extended model */
    bool coef_by_prop;  /* only for extended model */

    bool calc_dist;     /* checkbox for calculating distances on-the-fly */
    bool calc_depth;    /* checkbox for calculating depths on-the-fly */
    bool impute_at_fit; /* checkbox for producing imputed missing values on-the-fly */

    UseDepthImp   depth_imp;      /* only when building NA imputer */
    WeighImpRows  weigh_imp_rows; /* only when building NA imputer */
    size_t        min_imp_obs;    /* only when building NA imputer */
} ModelParams;

template <class sparse_ix=size_t>
struct ImputedData {
    std::vector<long double>  num_sum;
    std::vector<long double>  num_weight;
    std::vector<std::vector<long double>> cat_sum;
    std::vector<long double>  cat_weight;
    std::vector<long double>  sp_num_sum;
    std::vector<long double>  sp_num_weight;

    std::vector<size_t>     missing_num;
    std::vector<size_t>     missing_cat;
    std::vector<sparse_ix>  missing_sp;
    size_t                  n_missing_num;
    size_t                  n_missing_cat;
    size_t                  n_missing_sp;

    ImputedData() {};

    template <class InputData>
    ImputedData(InputData &input_data, size_t row)
    {
        initialize_impute_calc(*this, input_data, row);
    };

};

/*  This class provides efficient methods for sampling columns at random,
    given that at a given node a column might no longer be splittable,
    and when that happens, it also makes it non-splittable in any children
    node from there onwards. The idea is to provide efficient methods for
    passing the state from a parent node to a left node and then restore
    the state before going for the right node.
    It can be used in 3 modes:
    - As a uniform sampler with replacement.
    - As a weighted sampler with replacement.
    - As an array that keeps track of which columns are still splittable. */
class ColumnSampler
{
public:
    std::vector<size_t> col_indices;
    std::vector<double> tree_weights;
    size_t curr_pos;
    size_t curr_col;
    size_t last_given;
    size_t n_cols;
    size_t tree_levels;
    size_t offset;
    size_t n_dropped;
    template <class real_t=double>
    void initialize(real_t weights[], size_t n_cols);
    void initialize(size_t n_cols);
    void drop_weights();
    void leave_m_cols(size_t m, RNG_engine &rnd_generator);
    bool sample_col(size_t &col, RNG_engine &rnd_generator);
    void prepare_full_pass();        /* when passing through all columns */
    bool sample_col(size_t &col); /* when passing through all columns */
    void drop_col(size_t col);
    void shuffle_remainder(RNG_engine &rnd_generator);
    bool has_weights();
    size_t get_remaining_cols();
    ColumnSampler() = default;
};

template <class ImputedData>
struct WorkerMemory {
    std::vector<size_t>  ix_arr;
    std::vector<size_t>  ix_all;
    RNG_engine           rnd_generator;
    std::uniform_real_distribution<double> rbin;
    size_t               st;
    size_t               end;
    size_t               st_NA;
    size_t               end_NA;
    size_t               split_ix;
    std::unordered_map<size_t, double> weights_map;
    std::vector<double>  weights_arr;    /* when not ignoring NAs and when using weights as density */
    double               xmin;
    double               xmax;
    size_t               npresent;       /* 'npresent' and 'ncols_tried' are used interchangeable and for unrelated things */
    bool                 unsplittable;
    std::vector<bool>    is_repeated;
    std::vector<char>    categs;
    size_t               ncols_tried;    /* 'npresent' and 'ncols_tried' are used interchangeable and for unrelated things */
    int                  ncat_tried;
    std::vector<double>  btree_weights;  /* only when using weights for sampling */
    ColumnSampler        col_sampler;    /* columns can get eliminated, keep a copy for each thread */

    /* for split criterion */
    std::vector<double>  buffer_dbl;
    std::vector<size_t>  buffer_szt;
    std::vector<char>    buffer_chr;
    double               prob_split_type;
    GainCriterion        criterion;
    double               this_gain;
    double               this_split_point;
    int                  this_categ;
    std::vector<char>    this_split_categ;
    bool                 determine_split;

    /* for the extended model */
    size_t   ntry;
    size_t   ntaken;
    size_t   ntaken_best;
    size_t   ntried;
    bool     try_all;
    size_t   col_chosen; /* also used as placeholder in the single-variable model */
    ColType  col_type;
    double   ext_sd;
    std::vector<double>  comb_val;
    std::vector<size_t>  col_take;
    std::vector<ColType> col_take_type;
    std::vector<double>  ext_offset;
    std::vector<double>  ext_coef;
    std::vector<double>  ext_mean;
    std::vector<double>  ext_fill_val;
    std::vector<double>  ext_fill_new;
    std::vector<int>     chosen_cat;
    std::vector<std::vector<double>>       ext_cat_coef;
    std::uniform_real_distribution<double> coef_unif;
    std::normal_distribution<double>       coef_norm;
    std::vector<double> sample_weights; /* when using weights and split criterion */

    /* for similarity/distance calculations */
    std::vector<double> tmat_sep;

    /* when calculating average depth on-the-fly */
    std::vector<double> row_depths;

    /* when imputing NAs on-the-fly */
    std::vector<ImputedData> impute_vec;
    std::unordered_map<size_t, ImputedData> impute_map;

};

typedef struct WorkerForSimilarity {
    std::vector<size_t> ix_arr;
    size_t              st;
    size_t              end;
    std::vector<double> weights_arr;
    std::vector<double> comb_val;
    std::vector<double> tmat_sep;
    std::vector<double> rmat;
    size_t              n_from;
    bool                assume_full_distr; /* doesn't need to have one copy per worker */
} WorkerForSimilarity;

typedef struct WorkerForPredictCSC {
    std::vector<size_t> ix_arr;
    size_t              st;
    size_t              end;
    std::vector<double> comb_val;
    std::vector<double> weights_arr;
    std::vector<double> depths;
} WorkerForPredictCSC;

class RecursionState {
public:
    size_t  st;
    size_t  st_NA;
    size_t  end_NA;
    size_t  split_ix;
    size_t  end;
    size_t  sampler_pos;
    size_t  n_dropped;
    bool    full_state;
    std::vector<size_t> ix_arr;
    std::vector<bool>   cols_possible;
    std::vector<double> col_sampler_weights;
    std::unique_ptr<double[]> weights_arr;

    RecursionState() = default;
    template <class WorkerMemory>
    RecursionState(WorkerMemory &workspace, bool full_state);
    template <class WorkerMemory>
    void restore_state(WorkerMemory &workspace);
};

/* Function prototypes */

/* fit_model.cpp */
template <class real_t, class sparse_ix>
int fit_iforest(IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                real_t numeric_data[],  size_t ncols_numeric,
                int    categ_data[],    size_t ncols_categ,    int ncat[],
                real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                size_t ndim, size_t ntry, CoefType coef_type, bool coef_by_prop,
                real_t sample_weights[], bool with_replacement, bool weight_as_sample,
                size_t nrows, size_t sample_size, size_t ntrees,
                size_t max_depth, size_t ncols_per_tree,
                bool   limit_depth, bool penalize_range,
                bool   standardize_dist, double tmat[],
                double output_depths[], bool standardize_depth,
                real_t col_weights[], bool weigh_by_kurt,
                double prob_pick_by_gain_avg, double prob_split_by_gain_avg,
                double prob_pick_by_gain_pl,  double prob_split_by_gain_pl,
                double min_gain, MissingAction missing_action,
                CategSplit cat_split_type, NewCategAction new_cat_action,
                bool   all_perm, Imputer *imputer, size_t min_imp_obs,
                UseDepthImp depth_imp, WeighImpRows weigh_imp_rows, bool impute_at_fit,
                uint64_t random_seed, int nthreads);
template <class real_t, class sparse_ix>
int add_tree(IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
             real_t numeric_data[],  size_t ncols_numeric,
             int    categ_data[],    size_t ncols_categ,    int ncat[],
             real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
             size_t ndim, size_t ntry, CoefType coef_type, bool coef_by_prop,
             real_t sample_weights[], size_t nrows,
             size_t max_depth,     size_t ncols_per_tree,
             bool   limit_depth,   bool penalize_range,
             real_t col_weights[], bool weigh_by_kurt,
             double prob_pick_by_gain_avg, double prob_split_by_gain_avg,
             double prob_pick_by_gain_pl,  double prob_split_by_gain_pl,
             double min_gain, MissingAction missing_action,
             CategSplit cat_split_type, NewCategAction new_cat_action,
             UseDepthImp depth_imp, WeighImpRows weigh_imp_rows,
             bool   all_perm, std::vector<ImputeNode> *impute_nodes, size_t min_imp_obs,
             uint64_t random_seed);
template <class InputData, class WorkerMemory>
void fit_itree(std::vector<IsoTree>    *tree_root,
               std::vector<IsoHPlane>  *hplane_root,
               WorkerMemory             &workspace,
               InputData                &input_data,
               ModelParams              &model_params,
               std::vector<ImputeNode> *impute_nodes,
               size_t                   tree_num);

/* isoforest.cpp */
template <class InputData, class WorkerMemory>
void split_itree_recursive(std::vector<IsoTree>     &trees,
                           WorkerMemory             &workspace,
                           InputData                &input_data,
                           ModelParams              &model_params,
                           std::vector<ImputeNode> *impute_nodes,
                           size_t                   curr_depth);

/* extended.cpp */
template <class InputData, class WorkerMemory>
void split_hplane_recursive(std::vector<IsoHPlane>   &hplanes,
                            WorkerMemory             &workspace,
                            InputData                &input_data,
                            ModelParams              &model_params,
                            std::vector<ImputeNode> *impute_nodes,
                            size_t                   curr_depth);
template <class InputData, class WorkerMemory>
void add_chosen_column(WorkerMemory &workspace, InputData &input_data, ModelParams &model_params,
                       std::vector<bool> &col_is_taken, std::unordered_set<size_t> &col_is_taken_s);
void shrink_to_fit_hplane(IsoHPlane &hplane, bool clear_vectors);
template <class InputData, class WorkerMemory>
void simplify_hplane(IsoHPlane &hplane, WorkerMemory &workspace, InputData &input_data, ModelParams &model_params);


/* predict.cpp */
template <class real_t, class sparse_ix>
void predict_iforest(real_t numeric_data[], int categ_data[],
                     bool is_col_major, size_t ncols_numeric, size_t ncols_categ,
                     real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                     real_t Xr[], sparse_ix Xr_ind[], sparse_ix Xr_indptr[],
                     size_t nrows, int nthreads, bool standardize,
                     IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                     double output_depths[],   sparse_ix tree_num[]);
template <class PredictionData, class sparse_ix>
void traverse_itree_no_recurse(std::vector<IsoTree>  &tree,
                               IsoForest             &model_outputs,
                               PredictionData        &prediction_data,
                               double                &output_depth,
                               sparse_ix *restrict   tree_num,
                               size_t                row);
template <class PredictionData, class sparse_ix, class ImputedData>
double traverse_itree(std::vector<IsoTree>     &tree,
                      IsoForest                &model_outputs,
                      PredictionData           &prediction_data,
                      std::vector<ImputeNode> *impute_nodes,
                      ImputedData             *imputed_data,
                      double                   curr_weight,
                      size_t                   row,
                      sparse_ix *restrict      tree_num,
                      size_t                   curr_lev);
template <class PredictionData, class sparse_ix>
void traverse_hplane_fast(std::vector<IsoHPlane>  &hplane,
                          ExtIsoForest            &model_outputs,
                          PredictionData          &prediction_data,
                          double                  &output_depth,
                          sparse_ix *restrict     tree_num,
                          size_t                  row);
template <class PredictionData, class sparse_ix, class ImputedData>
void traverse_hplane(std::vector<IsoHPlane>   &hplane,
                     ExtIsoForest             &model_outputs,
                     PredictionData           &prediction_data,
                     double                   &output_depth,
                     std::vector<ImputeNode> *impute_nodes,
                     ImputedData             *imputed_data,
                     sparse_ix *restrict      tree_num,
                     size_t                   row);
template <class PredictionData, class sparse_ix>
void traverse_itree_csc(WorkerForPredictCSC   &workspace,
                        std::vector<IsoTree>  &trees,
                        IsoForest             &model_outputs,
                        PredictionData        &prediction_data,
                        sparse_ix             *tree_num,
                        size_t                curr_tree,
                        bool                  has_range_penalty);
template <class PredictionData, class sparse_ix>
void traverse_hplane_csc(WorkerForPredictCSC      &workspace,
                         std::vector<IsoHPlane>   &hplanes,
                         ExtIsoForest             &model_outputs,
                         PredictionData           &prediction_data,
                         sparse_ix                *tree_num,
                         size_t                   curr_tree,
                         bool                     has_range_penalty);
template <class PredictionData>
void add_csc_range_penalty(WorkerForPredictCSC  &workspace,
                           PredictionData       &prediction_data,
                           double               *weights_arr,
                           size_t               col_num,
                           double               range_low,
                           double               range_high);
template <class PredictionData>
double extract_spC(PredictionData &prediction_data, size_t row, size_t col_num);
template <class PredictionData, class sparse_ix>
double extract_spR(PredictionData &prediction_data, sparse_ix *row_st, sparse_ix *row_end, size_t col_num);
template <class sparse_ix>
void get_num_nodes(IsoForest &model_outputs, sparse_ix *restrict n_nodes, sparse_ix *restrict n_terminal, int nthreads);
template <class sparse_ix>
void get_num_nodes(ExtIsoForest &model_outputs, sparse_ix *restrict n_nodes, sparse_ix *restrict n_terminal, int nthreads);

/* dist.cpp */
template <class real_t, class sparse_ix>
void calc_similarity(real_t numeric_data[], int categ_data[],
                     real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                     size_t nrows, int nthreads, bool assume_full_distr, bool standardize_dist,
                     IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                     double tmat[], double rmat[], size_t n_from);
template <class PredictionData>
void traverse_tree_sim(WorkerForSimilarity   &workspace,
                       PredictionData        &prediction_data,
                       IsoForest             &model_outputs,
                       std::vector<IsoTree>  &trees,
                       size_t                curr_tree);
template <class PredictionData>
void traverse_hplane_sim(WorkerForSimilarity     &workspace,
                         PredictionData          &prediction_data,
                         ExtIsoForest            &model_outputs,
                         std::vector<IsoHPlane>  &hplanes,
                         size_t                  curr_tree);
template <class PredictionData, class InputData, class WorkerMemory>
void gather_sim_result(std::vector<WorkerForSimilarity> *worker_memory,
                       std::vector<WorkerMemory> *worker_memory_m,
                       PredictionData *prediction_data, InputData *input_data,
                       IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                       double *restrict tmat, double *restrict rmat, size_t n_from,
                       size_t ntrees, bool assume_full_distr,
                       bool standardize_dist, int nthreads);
template <class PredictionData>
void initialize_worker_for_sim(WorkerForSimilarity  &workspace,
                               PredictionData       &prediction_data,
                               IsoForest            *model_outputs,
                               ExtIsoForest         *model_outputs_ext,
                               size_t                n_from,
                               bool                  assume_full_distr);

/* impute.cpp */
template <class real_t, class sparse_ix>
void impute_missing_values(real_t numeric_data[], int categ_data[], bool is_col_major,
                           real_t Xr[], sparse_ix Xr_ind[], sparse_ix Xr_indptr[],
                           size_t nrows, int nthreads,
                           IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                           Imputer &imputer);
template <class InputData>
void initialize_imputer(Imputer &imputer, InputData &input_data, size_t ntrees, int nthreads);
template <class InputData, class WorkerMemory>
void build_impute_node(ImputeNode &imputer,    WorkerMemory &workspace,
                       InputData  &input_data, ModelParams  &model_params,
                       std::vector<ImputeNode> &imputer_tree,
                       size_t curr_depth, size_t min_imp_obs);
void shrink_impute_node(ImputeNode &imputer);
void drop_nonterminal_imp_node(std::vector<ImputeNode>  &imputer_tree,
                               std::vector<IsoTree>     *trees,
                               std::vector<IsoHPlane>   *hplanes);
template <class ImputedData>
void combine_imp_single(ImputedData &imp_addfrom, ImputedData &imp_addto);
template <class ImputedData, class WorkerMemory>
void combine_tree_imputations(WorkerMemory &workspace,
                              std::vector<ImputedData> &impute_vec,
                              std::unordered_map<size_t, ImputedData> &impute_map,
                              std::vector<char> &has_missing,
                              int nthreads);
template <class ImputedData>
void add_from_impute_node(ImputeNode &imputer, ImputedData &imputed_data, double w);
template <class InputData, class WorkerMemory>
void add_from_impute_node(ImputeNode &imputer, WorkerMemory &workspace, InputData &input_data);
template <class imp_arr, class InputData>
void apply_imputation_results(imp_arr    &impute_vec,
                              Imputer    &imputer,
                              InputData  &input_data,
                              int        nthreads);
template <class ImputedData, class InputData>
void apply_imputation_results(std::vector<ImputedData> &impute_vec,
                              std::unordered_map<size_t, ImputedData> &impute_map,
                              Imputer   &imputer,
                              InputData &input_data,
                              int nthreads);
template <class PredictionData, class ImputedData>
void apply_imputation_results(PredictionData  &prediction_data,
                              ImputedData     &imp,
                              Imputer         &imputer,
                              size_t          row);
template <class ImputedData, class InputData>
void initialize_impute_calc(ImputedData &imp, InputData &input_data, size_t row);
template <class ImputedData, class PredictionData>
void initialize_impute_calc(ImputedData &imp, PredictionData &prediction_data, Imputer &imputer, size_t row);
template <class ImputedData, class InputData>
void allocate_imp_vec(std::vector<ImputedData> &impute_vec, InputData &input_data, int nthreads);
template <class ImputedData, class InputData>
void allocate_imp_map(std::unordered_map<size_t, ImputedData> &impute_map, InputData &input_data);
template <class ImputedData, class InputData>
void allocate_imp(InputData &input_data,
                  std::vector<ImputedData> &impute_vec,
                  std::unordered_map<size_t, ImputedData> &impute_map,
                  int nthreads);
template <class ImputedData, class InputData>
void check_for_missing(InputData &input_data,
                       std::vector<ImputedData> &impute_vec,
                       std::unordered_map<size_t, ImputedData> &impute_map,
                       int nthreads);
template <class PredictionData>
size_t check_for_missing(PredictionData  &prediction_data,
                         Imputer         &imputer,
                         size_t          ix_arr[],
                         int             nthreads);

/* helpers_iforest.cpp */
template <class InputData, class WorkerMemory>
void get_split_range(WorkerMemory &workspace, InputData &input_data, ModelParams &model_params, IsoTree &tree);
template <class InputData, class WorkerMemory>
void get_split_range(WorkerMemory &workspace, InputData &input_data, ModelParams &model_params);
template <class InputData, class WorkerMemory>
int choose_cat_from_present(WorkerMemory &workspace, InputData &input_data, size_t col_num);
bool is_col_taken(std::vector<bool> &col_is_taken, std::unordered_set<size_t> &col_is_taken_s,
                  size_t col_num);
template <class InputData>
void set_col_as_taken(std::vector<bool> &col_is_taken, std::unordered_set<size_t> &col_is_taken_s,
                      InputData &input_data, size_t col_num, ColType col_type);
template <class InputData, class WorkerMemory>
void add_separation_step(WorkerMemory &workspace, InputData &input_data, double remainder);
template <class InputData, class WorkerMemory>
void add_remainder_separation_steps(WorkerMemory &workspace, InputData &input_data, long double sum_weight);
template <class PredictionData, class sparse_ix>
void remap_terminal_trees(IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                          PredictionData &prediction_data, sparse_ix *restrict tree_num, int nthreads);


/* utils.cpp */
size_t log2ceil(size_t x);
double digamma(double x);
double harmonic(size_t n);
double harmonic_recursive(double a, double b);
double expected_avg_depth(size_t sample_size);
double expected_avg_depth(long double approx_sample_size);
double expected_separation_depth(size_t n);
double expected_separation_depth_hotstart(double curr, size_t n_curr, size_t n_final);
double expected_separation_depth(long double n);
void increase_comb_counter(size_t ix_arr[], size_t st, size_t end, size_t n, double counter[], double exp_remainder);
void increase_comb_counter(size_t ix_arr[], size_t st, size_t end, size_t n,
                           double *restrict counter, double *restrict weights, double exp_remainder);
void increase_comb_counter(size_t ix_arr[], size_t st, size_t end, size_t n,
                           double counter[], std::unordered_map<size_t, double> &weights, double exp_remainder);
void increase_comb_counter_in_groups(size_t ix_arr[], size_t st, size_t end, size_t split_ix, size_t n,
                                     double counter[], double exp_remainder);
void increase_comb_counter_in_groups(size_t ix_arr[], size_t st, size_t end, size_t split_ix, size_t n,
                                     double *restrict counter, double *restrict weights, double exp_remainder);
void tmat_to_dense(double *restrict tmat, double *restrict dmat, size_t n, bool diag_to_one);
template <class real_t=double>
void build_btree_sampler(std::vector<double> &btree_weights, real_t *restrict sample_weights,
                         size_t nrows, size_t &log2_n, size_t &btree_offset);
template <class real_t=double>
void sample_random_rows(std::vector<size_t> &ix_arr, size_t nrows, bool with_replacement,
                        RNG_engine &rnd_generator, std::vector<size_t> &ix_all,
                        real_t sample_weights[], std::vector<double> &btree_weights,
                        size_t log2_n, size_t btree_offset, std::vector<bool> &is_repeated);
template <class real_t=double>
void weighted_shuffle(size_t *restrict outp, size_t n, real_t *restrict weights, double *restrict buffer_arr, RNG_engine &rnd_generator);
size_t divide_subset_split(size_t ix_arr[], double x[], size_t st, size_t end, double split_point);
template <class real_t=double>
void divide_subset_split(size_t ix_arr[], real_t x[], size_t st, size_t end, double split_point,
                         MissingAction missing_action, size_t &st_NA, size_t &end_NA, size_t &split_ix);
template <class real_t, class sparse_ix>
void divide_subset_split(size_t ix_arr[], size_t st, size_t end, size_t col_num,
                         real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[], double split_point,
                         MissingAction missing_action, size_t &st_NA, size_t &end_NA, size_t &split_ix);
void divide_subset_split(size_t ix_arr[], int x[], size_t st, size_t end, char split_categ[],
                         MissingAction missing_action, size_t &st_NA, size_t &end_NA, size_t &split_ix);
void divide_subset_split(size_t ix_arr[], int x[], size_t st, size_t end, char split_categ[],
                         int ncat, MissingAction missing_action, NewCategAction new_cat_action,
                         bool move_new_to_left, size_t &st_NA, size_t &end_NA, size_t &split_ix);
void divide_subset_split(size_t ix_arr[], int x[], size_t st, size_t end, int split_categ,
                         MissingAction missing_action, size_t &st_NA, size_t &end_NA, size_t &split_ix);
void divide_subset_split(size_t ix_arr[], int x[], size_t st, size_t end,
                         MissingAction missing_action, NewCategAction new_cat_action,
                         bool move_new_to_left, size_t &st_NA, size_t &end_NA, size_t &split_ix);
template <class real_t=double>
void get_range(size_t ix_arr[], real_t x[], size_t st, size_t end,
               MissingAction missing_action, double &xmin, double &xmax, bool &unsplittable);
template <class real_t, class sparse_ix>
void get_range(size_t ix_arr[], size_t st, size_t end, size_t col_num,
               real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
               MissingAction missing_action, double &xmin, double &xmax, bool &unsplittable);
void get_categs(size_t ix_arr[], int x[], size_t st, size_t end, int ncat,
                MissingAction missing_action, char categs[], size_t &npresent, bool &unsplittable);
long double calculate_sum_weights(std::vector<size_t> &ix_arr, size_t st, size_t end, size_t curr_depth,
                                  std::vector<double> &weights_arr, std::unordered_map<size_t, double> &weights_map);
extern bool interrupt_switch;
extern bool signal_is_locked;
void set_interrup_global_variable(int s);
#ifdef _FOR_PYTHON
bool cy_check_interrupt_switch();
void cy_tick_off_interrupt_switch();
#endif
class SignalSwitcher
{
public:
    sig_t_ old_sig;
    bool is_active;
    SignalSwitcher();
    ~SignalSwitcher();
    void restore_handle();
};
void check_interrupt_switch(SignalSwitcher &ss);
int return_EXIT_SUCCESS();
int return_EXIT_FAILURE();



template <class real_t=double>
size_t move_NAs_to_front(size_t ix_arr[], size_t st, size_t end, real_t x[]);
template <class real_t, class sparse_ix>
size_t move_NAs_to_front(size_t ix_arr[], size_t st, size_t end, size_t col_num, real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[]);
size_t move_NAs_to_front(size_t ix_arr[], size_t st, size_t end, int x[]);
size_t center_NAs(size_t *restrict ix_arr, size_t st_left, size_t st, size_t curr_pos);
template <class real_t, class sparse_ix>
void todense(size_t ix_arr[], size_t st, size_t end,
             size_t col_num, real_t *restrict Xc, sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
             double *restrict buffer_arr);
template <class sparse_ix=size_t>
bool check_indices_are_sorted(sparse_ix indices[], size_t n);
template <class real_t, class sparse_ix>
void sort_csc_indices(real_t *restrict Xc, sparse_ix *restrict Xc_ind, sparse_ix *restrict Xc_indptr, size_t ncols_numeric);

/* mult.cpp */
template <class real_t, class real_t_>
void calc_mean_and_sd_t(size_t ix_arr[], size_t st, size_t end, real_t_ *restrict x,
                        MissingAction missing_action, double &x_sd, double &x_mean);
template <class real_t_>
void calc_mean_and_sd(size_t ix_arr[], size_t st, size_t end, real_t_ *restrict x,
                      MissingAction missing_action, double &x_sd, double &x_mean);
template <class real_t_, class mapping>
void calc_mean_and_sd_weighted(size_t ix_arr[], size_t st, size_t end, real_t_ *restrict x, mapping w,
                               MissingAction missing_action, double &x_sd, double &x_mean);
template <class real_t_, class sparse_ix>
void calc_mean_and_sd(size_t ix_arr[], size_t st, size_t end, size_t col_num,
                      real_t_ *restrict Xc, sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                      double &x_sd, double &x_mean);
template <class real_t_, class sparse_ix, class mapping>
void calc_mean_and_sd_weighted(size_t ix_arr[], size_t st, size_t end, size_t col_num,
                               real_t_ *restrict Xc, sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                               double &x_sd, double &x_mean, mapping w);
template <class real_t_>
void add_linear_comb(size_t ix_arr[], size_t st, size_t end, double *restrict res,
                     real_t_ *restrict x, double &coef, double x_sd, double x_mean, double &fill_val,
                     MissingAction missing_action, double *restrict buffer_arr,
                     size_t *restrict buffer_NAs, bool first_run);
template <class real_t_, class mapping>
void add_linear_comb_weighted(size_t ix_arr[], size_t st, size_t end, double *restrict res,
                              real_t_ *restrict x, double &coef, double x_sd, double x_mean, double &fill_val,
                              MissingAction missing_action, double *restrict buffer_arr,
                              size_t *restrict buffer_NAs, bool first_run, mapping w);
template <class real_t_, class sparse_ix>
void add_linear_comb(size_t *restrict ix_arr, size_t st, size_t end, size_t col_num, double *restrict res,
                     real_t_ *restrict Xc, sparse_ix *restrict Xc_ind, sparse_ix *restrict Xc_indptr,
                     double &coef, double x_sd, double x_mean, double &fill_val, MissingAction missing_action,
                     double *restrict buffer_arr, size_t *restrict buffer_NAs, bool first_run);
template <class real_t_, class sparse_ix, class mapping>
void add_linear_comb_weighted(size_t *restrict ix_arr, size_t st, size_t end, size_t col_num, double *restrict res,
                              real_t_ *restrict Xc, sparse_ix *restrict Xc_ind, sparse_ix *restrict Xc_indptr,
                              double &coef, double x_sd, double x_mean, double &fill_val, MissingAction missing_action,
                              double *restrict buffer_arr, size_t *restrict buffer_NAs, bool first_run, mapping w);
void add_linear_comb(size_t *restrict ix_arr, size_t st, size_t end, double *restrict res,
                     int x[], int ncat, double *restrict cat_coef, double single_cat_coef, int chosen_cat,
                     double &fill_val, double &fill_new, size_t *restrict buffer_cnt, size_t *restrict buffer_pos,
                     NewCategAction new_cat_action, MissingAction missing_action, CategSplit cat_split_type, bool first_run);
template <class mapping>
void add_linear_comb_weighted(size_t *restrict ix_arr, size_t st, size_t end, double *restrict res,
                              int x[], int ncat, double *restrict cat_coef, double single_cat_coef, int chosen_cat,
                              double &fill_val, double &fill_new, size_t *restrict buffer_pos,
                              NewCategAction new_cat_action, MissingAction missing_action, CategSplit cat_split_type,
                              bool first_run, mapping w);

/* crit.cpp */
template <class real_t=double>
double calc_kurtosis(size_t ix_arr[], size_t st, size_t end, real_t x[], MissingAction missing_action);
template <class real_t, class mapping>
double calc_kurtosis_weighted(size_t ix_arr[], size_t st, size_t end, real_t x[],
                              MissingAction missing_action, mapping w);
template <class real_t, class sparse_ix>
double calc_kurtosis(size_t ix_arr[], size_t st, size_t end, size_t col_num,
                     real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                     MissingAction missing_action);
template <class real_t, class sparse_ix, class mapping>
double calc_kurtosis_weighted(size_t ix_arr[], size_t st, size_t end, size_t col_num,
                              real_t Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                              MissingAction missing_action, mapping w);
double calc_kurtosis(size_t ix_arr[], size_t st, size_t end, int x[], int ncat, size_t buffer_cnt[], double buffer_prob[],
                     MissingAction missing_action, CategSplit cat_split_type, RNG_engine &rnd_generator);
template <class mapping>
double calc_kurtosis_weighted(size_t ix_arr[], size_t st, size_t end, int x[], int ncat, double buffer_prob[],
                              MissingAction missing_action, CategSplit cat_split_type, RNG_engine &rnd_generator, mapping w);
double expected_sd_cat(double p[], size_t n, size_t pos[]);
template <class number>
double expected_sd_cat(number counts[], double p[], size_t n, size_t pos[]);
template <class number>
double expected_sd_cat_single(number counts[], double p[], size_t n, size_t pos[], size_t cat_exclude, number cnt);
template <class number>
double categ_gain(number cnt_left, number cnt_right,
                  long double s_left, long double s_right,
                  long double base_info, long double cnt);
template <class real_t, class real_t_=double>
double find_split_rel_gain_t(real_t_ *restrict x, size_t n, double &split_point);
template <class real_t_=double>
double find_split_rel_gain(real_t_ *restrict x, size_t n, double &split_point);
template <class real_t, class real_t_>
double find_split_rel_gain_t(real_t_ *restrict x, real_t_ xmean, size_t ix_arr[], size_t st, size_t end, double &split_point, size_t &split_ix);
template <class real_t_=double>
double find_split_rel_gain(real_t_ *restrict x, real_t_ xmean, size_t ix_arr[], size_t st, size_t end, double &split_point, size_t &split_ix);
template <class real_t, class real_t_=double>
real_t calc_sd_right_to_left(real_t_ *restrict x, size_t n, double *restrict sd_arr);
template <class real_t_>
long double calc_sd_right_to_left_weighted(real_t_ *restrict x, size_t n, double *restrict sd_arr,
                                           double *restrict w, long double &cumw, size_t *restrict sorted_ix);
template <class real_t, class real_t_>
real_t calc_sd_right_to_left(real_t_ *restrict x, real_t_ xmean, size_t ix_arr[], size_t st, size_t end, double *restrict sd_arr);
template <class real_t_, class mapping>
long double calc_sd_right_to_left_weighted(real_t_ *restrict x, real_t_ xmean, size_t ix_arr[], size_t st, size_t end,
                                           double *restrict sd_arr, mapping w, long double &cumw);
template <class real_t, class real_t_>
double find_split_std_gain_t(real_t_ *restrict x, size_t n, double *restrict sd_arr,
                             GainCriterion criterion, double min_gain, double &split_point);
template <class real_t_=double>
double find_split_std_gain(real_t_ *restrict x, size_t n, double *restrict sd_arr,
                           GainCriterion criterion, double min_gain, double &split_point);
template <class real_t>
double find_split_std_gain_weighted(real_t *restrict x, size_t n, double *restrict sd_arr,
                                    GainCriterion criterion, double min_gain, double &split_point,
                                    double *restrict w, size_t *restrict sorted_ix);
template <class real_t, class real_t_>
double find_split_std_gain_t(real_t_ *restrict x, real_t_ xmean, size_t ix_arr[], size_t st, size_t end, double *restrict sd_arr,
                             GainCriterion criterion, double min_gain, double &split_point, size_t &split_ix);
template <class real_t_>
double find_split_std_gain(real_t_ *restrict x, real_t_ xmean, size_t ix_arr[], size_t st, size_t end, double *restrict sd_arr,
                           GainCriterion criterion, double min_gain, double &split_point, size_t &split_ix);
template <class real_t, class mapping>
double find_split_std_gain_weighted(real_t *restrict x, real_t xmean, size_t ix_arr[], size_t st, size_t end, double *restrict sd_arr,
                                    GainCriterion criterion, double min_gain, double &split_point, size_t &split_ix, mapping w);
double eval_guided_crit(double *restrict x, size_t n, GainCriterion criterion,
                        double min_gain, bool as_relative_gain, double *restrict buffer_sd,
                        double &split_point, double &xmin, double &xmax);
double eval_guided_crit_weighted(double *restrict x, size_t n, GainCriterion criterion,
                                 double min_gain, bool as_relative_gain, double *restrict buffer_sd,
                                 double &split_point, double &xmin, double &xmax,
                                 double *restrict w, size_t *restrict buffer_indices);
template <class real_t_>
double eval_guided_crit(size_t *restrict ix_arr, size_t st, size_t end, real_t_ *restrict x,
                        double *restrict buffer_sd, bool as_relative_gain,
                        size_t &split_ix, double &split_point, double &xmin, double &xmax,
                        GainCriterion criterion, double min_gain, MissingAction missing_action);
template <class real_t_, class mapping>
double eval_guided_crit_weighted(size_t *restrict ix_arr, size_t st, size_t end, real_t_ *restrict x,
                                 double *restrict buffer_sd, bool as_relative_gain,
                                 size_t &split_ix, double &split_point, double &xmin, double &xmax,
                                 GainCriterion criterion, double min_gain, MissingAction missing_action,
                                 mapping w);
template <class real_t_, class sparse_ix>
double eval_guided_crit(size_t ix_arr[], size_t st, size_t end,
                        size_t col_num, real_t_ Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                        double buffer_arr[], size_t buffer_pos[], bool as_relative_gain,
                        double &split_point, double &xmin, double &xmax,
                        GainCriterion criterion, double min_gain, MissingAction missing_action);
template <class real_t_, class sparse_ix, class mapping>
double eval_guided_crit_weighted(size_t ix_arr[], size_t st, size_t end,
                                 size_t col_num, real_t_ Xc[], sparse_ix Xc_ind[], sparse_ix Xc_indptr[],
                                 double buffer_arr[], size_t buffer_pos[], bool as_relative_gain,
                                 double &split_point, double &xmin, double &xmax,
                                 GainCriterion criterion, double min_gain, MissingAction missing_action,
                                 mapping w);
double eval_guided_crit(size_t *restrict ix_arr, size_t st, size_t end, int *restrict x, int ncat,
                        size_t *restrict buffer_cnt, size_t *restrict buffer_pos, double *restrict buffer_prob,
                        int &chosen_cat, char *restrict split_categ, char *restrict buffer_split,
                        GainCriterion criterion, double min_gain, bool all_perm,
                        MissingAction missing_action, CategSplit cat_split_type);
template <class mapping>
double eval_guided_crit_weighted(size_t *restrict ix_arr, size_t st, size_t end, int *restrict x, int ncat,
                                 size_t *restrict buffer_pos, double *restrict buffer_prob,
                                 int &chosen_cat, char *restrict split_categ, char *restrict buffer_split,
                                 GainCriterion criterion, double min_gain, bool all_perm,
                                 MissingAction missing_action, CategSplit cat_split_type,
                                 mapping w);

/* merge_models.cpp */
void merge_models(IsoForest*     model,      IsoForest*     other,
                  ExtIsoForest*  ext_model,  ExtIsoForest*  ext_other,
                  Imputer*       imputer,    Imputer*       iother);

#if defined(_ENABLE_CEREAL) || defined(_FOR_PYTHON)
/* serialize.cpp */
void serialize_isoforest(IsoForest &model, std::ostream &output);
void serialize_isoforest(IsoForest &model, const char *output_file_path);
std::string serialize_isoforest(IsoForest &model);
void deserialize_isoforest(IsoForest &output_obj, std::istream &serialized);
void deserialize_isoforest(IsoForest &output_obj, const char *input_file_path);
void deserialize_isoforest(IsoForest &output_obj, std::string &serialized, bool move_str);
void serialize_ext_isoforest(ExtIsoForest &model, std::ostream &output);
void serialize_ext_isoforest(ExtIsoForest &model, const char *output_file_path);
std::string serialize_ext_isoforest(ExtIsoForest &model);
void deserialize_ext_isoforest(ExtIsoForest &output_obj, std::istream &serialized);
void deserialize_ext_isoforest(ExtIsoForest &output_obj, const char *input_file_path);
void deserialize_ext_isoforest(ExtIsoForest &output_obj, std::string &serialized, bool move_str);
void serialize_imputer(Imputer &imputer, std::ostream &output);
void serialize_imputer(Imputer &imputer, const char *output_file_path);
std::string serialize_imputer(Imputer &imputer);
void deserialize_imputer(Imputer &output_obj, std::istream &serialized);
void deserialize_imputer(Imputer &output_obj, const char *input_file_path);
void deserialize_imputer(Imputer &output_obj, std::string &serialized, bool move_str);
#ifdef _MSC_VER
void serialize_isoforest(IsoForest &model, const wchar_t *output_file_path);
void deserialize_isoforest(IsoForest &output_obj, const wchar_t *input_file_path);
void serialize_ext_isoforest(ExtIsoForest &model, const wchar_t *output_file_path);
void deserialize_ext_isoforest(ExtIsoForest &output_obj, const wchar_t *input_file_path);
void serialize_imputer(Imputer &imputer, const wchar_t *output_file_path);
void deserialize_imputer(Imputer &output_obj, const wchar_t *input_file_path);
#endif /* _MSC_VER */
bool has_msvc();
#ifdef _FOR_PYTHON
void serialize_isoforest(IsoForest &model, void *output_file_path);
void deserialize_isoforest(IsoForest &output_obj, void *input_file_path);
void serialize_ext_isoforest(ExtIsoForest &model, void *output_file_path);
void deserialize_ext_isoforest(ExtIsoForest &output_obj, void *input_file_path);
void serialize_imputer(Imputer &imputer, void *output_file_path);
void deserialize_imputer(Imputer &output_obj, void *input_file_path);
bool py_should_use_char();
bool has_cereal();
#endif /* _FOR_PYTHON */
#endif /* _ENABLE_CEREAL || _FOR_PYTON */

/* sql.cpp */
std::vector<std::string> generate_sql(IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                                      std::vector<std::string> &numeric_colnames, std::vector<std::string> &categ_colnames,
                                      std::vector<std::vector<std::string>> &categ_levels,
                                      bool output_tree_num, bool index1, bool single_tree, size_t tree_num,
                                      int nthreads);
std::string generate_sql_with_select_from(IsoForest *model_outputs, ExtIsoForest *model_outputs_ext,
                                          std::string &table_from, std::string &select_as,
                                          std::vector<std::string> &numeric_colnames, std::vector<std::string> &categ_colnames,
                                          std::vector<std::vector<std::string>> &categ_levels,
                                          bool index1, int nthreads);
void generate_tree_rules(std::vector<IsoTree> *trees, std::vector<IsoHPlane> *hplanes, bool output_score,
                         size_t curr_ix, bool index1, std::string &prev_cond, std::vector<std::string> &node_rules,
                         std::vector<std::string> &conditions_left, std::vector<std::string> &conditions_right);
void extract_cond_isotree(IsoForest &model, IsoTree &tree,
                          std::string &cond_left, std::string &cond_right,
                          std::vector<std::string> &numeric_colnames, std::vector<std::string> &categ_colnames,
                          std::vector<std::vector<std::string>> &categ_levels);
void extract_cond_ext_isotree(ExtIsoForest &model, IsoHPlane &hplane,
                              std::string &cond_left, std::string &cond_right,
                              std::vector<std::string> &numeric_colnames, std::vector<std::string> &categ_colnames,
                              std::vector<std::vector<std::string>> &categ_levels);

#endif /* ISOTREE_H */
