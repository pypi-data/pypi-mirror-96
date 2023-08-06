import copy
import itertools
from abc import abstractmethod
from typing import Type

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.linalg import block_diag, eigh
from sklearn.base import BaseEstimator

import cca_zoo.data
import cca_zoo.innerloop
import cca_zoo.kcca
import cca_zoo.plot_utils


# from hyperopt import fmin, tpe, Trials

class CCA_Base(BaseEstimator):
    @abstractmethod
    def __init__(self, latent_dims: int = 1):
        self.train_correlations = None
        self.latent_dims = latent_dims

    @abstractmethod
    def fit(self, *views, **kwargs):
        """
        The fit method takes any number of views as a numpy array along with associated parameters as a dictionary.
        Returns a fit model object which can be used to predict correlations or transform out of sample data.
        :param views: 2D numpy arrays for each view separated by comma with the same number of rows (nxp)
        :param kwargs: parameters associated with the method.
        :return: training data correlations and the parameters required to call other functions in the class.
        """
        pass
        return self

    @abstractmethod
    def transform(self, *views):
        """
        The transform method takes any number of views as a numpy array. Need to have the same number of features as
        those in the views used to train the model.
        Returns the views transformed into the learnt latent space.
        :param views: numpy arrays separated by comma. Each view needs to have the same number of features as its
         corresponding view in the training data
        :return: tuple of transformed numpy arrays
        """
        pass
        return self

    def fit_transform(self, *views, **kwargs):
        """
        Apply fit and immediately transform the same data
        :param views:
        :param kwargs: parameters associated with the method
        :return: tuple of transformed numpy arrays
        """
        self.fit(*views, **kwargs).transform(*views)

    def predict_corr(self, *views):
        """
        :param views: numpy arrays separated by comma. Each view needs to have the same number of features as its
         corresponding view in the training data
        :return: numpy array containing correlations between each pair of views for each dimension (#views*#views*#latent_dimensions)
        """
        # Takes two views and predicts their out of sample correlation using trained model
        transformed_views = self.transform(*views)
        all_corrs = []
        for x, y in itertools.product(transformed_views, repeat=2):
            all_corrs.append(np.diag(np.corrcoef(x.T, y.T)[:self.latent_dims, self.latent_dims:]))
        all_corrs = np.array(all_corrs).reshape((len(views), len(views), self.latent_dims))
        return all_corrs

    def demean_data(self, *views):
        """
        Since most methods require zero-mean data, demean_data() is used to demean training data as well as to apply this
        demeaning transformation to out of sample data
        :param views:
        :return:
        """
        views_demeaned = []
        self.view_means = []
        for view in views:
            self.view_means.append(view.mean(axis=0))
            views_demeaned.append(view - view.mean(axis=0))
        return views_demeaned

    def gridsearch_fit(self, *views, param_candidates=None, folds: int = 5, verbose: bool = False, jobs: int = 0,
                       plot: bool = False):
        """
        Fits the model using a user defined grid search. Returns parameters/objects that allow out of sample transformation or prediction
        Supports parallel model training with jobs>0
        :param views: numpy arrays separated by comma e.g. fit(view_1,view_2,view_3)
        :param param_candidates: dictionary containing a list for each parameter where all lists have the same length.
        :param folds: number of folds used for cross validation
        :param verbose: whether to return scores for each set of parameters
        :return: fit model with best parameters
        """""
        if verbose:
            print('cross validation', flush=True)
            print('number of folds: ', folds, flush=True)

        # Set up an array for each set of hyperparameters
        assert (len(param_candidates) > 0)
        param_names = list(param_candidates.keys())
        param_values = list(param_candidates.values())
        param_combinations = list(itertools.product(*param_values))

        param_sets = []
        for param_set in param_combinations:
            param_dict = {}
            for i, param_name in enumerate(param_names):
                param_dict[param_name] = param_set[i]
            param_sets.append(param_dict)

        cv = CrossValidate(self, folds=folds, verbose=verbose)

        if jobs > 0:
            out = Parallel(n_jobs=jobs)(delayed(cv.score)(*views, **param_set) for param_set in param_sets)
        else:
            out = [cv.score(*views, **param_set) for param_set in param_sets]
        cv_scores, cv_stds = zip(*out)
        max_index = cv_scores.index(max(cv_scores))

        print('Best score : ', max(cv_scores), flush=True)
        print('Standard deviation : ', cv_stds[max_index], flush=True)
        print(param_sets[max_index], flush=True)

        self.cv_results_table = pd.DataFrame(zip(param_sets, cv_scores, cv_stds), columns=['params', 'scores', 'std'])
        self.cv_results_table = self.cv_results_table.join(pd.json_normalize(self.cv_results_table.params))
        self.cv_results_table.drop(columns=['params'], inplace=True)

        if plot:
            cca_zoo.plot_utils.cv_plot(cv_scores, param_sets, self.__class__.__name__)

        self.fit(*views, **param_sets[max_index])
        return self

    """
    def bayes_fit(self, *views, space=None, folds: int = 5, verbose=True):
        :param views: numpy arrays separated by comma e.g. fit(view_1,view_2,view_3)
        :param space:
        :param folds: number of folds used for cross validation
        :param verbose: whether to return scores for each set of parameters
        :return: fit model with best parameters
        trials = Trials()

        cv = CrossValidate(self, folds=folds, verbose=verbose)

        best_params = fmin(
            fn=cv.score(*views),
            space=space,
            algo=tpe.suggest,
            max_evals=100,
            trials=trials,
        )
        self.fit(*views, params=best_params)
        return self
    """


class KCCA(CCA_Base):
    def __init__(self, latent_dims: int = 1):
        super().__init__(latent_dims=latent_dims)

    def fit(self, *views, kernel: str = 'linear', sigma: float = 1.0, degree: int = 1, c=None):
        """
        The fit method takes any number of views as a numpy array along with associated parameters as a dictionary.
        Returns a fit model object which can be used to predict correlations or transform out of sample data.
        :param views: 2D numpy arrays for each view with the same number of rows (nxp)
        :param kernel: the kernel type 'linear', 'rbf', 'poly'
        :param sigma: sigma parameter used by sklearn rbf kernel
        :param degree: polynomial order parameter used by sklearn polynomial kernel
        :param c: regularisation between 0 (CCA) and 1 (PLS)
        :return: training data correlations and the parameters required to call other functions in the class.
        """
        self.c = c
        if self.c is None:
            self.c = [0] * len(views)
        assert (len(self.c) == len(views)), 'c requires as many values as #views'
        self.kernel = kernel
        self.sigma = sigma
        self.degree = degree
        self.model = cca_zoo.kcca.KCCA(*self.demean_data(*views), latent_dims=self.latent_dims, kernel=self.kernel,
                                       sigma=self.sigma,
                                       degree=self.degree, c=self.c)
        self.score_list = self.model.score_list
        self.train_correlations = self.predict_corr(*views)
        return self

    def transform(self, *views):
        # transformed_views = list(self.fit_kcca.transform(views[0] - self.view_means[0], views[1] - self.view_means[1]))
        # return transformed_views
        transformed_views = []
        for i, view in enumerate(views):
            transformed_views.append(
                self.model.make_kernel(view - self.view_means[i], self.model.views[i]) @ self.model.alphas[i])
        return transformed_views


class MCCA(CCA_Base):
    def __init__(self, latent_dims: int = 1):
        super().__init__(latent_dims=latent_dims)

    def fit(self, *views, c=None):
        """
        The fit method takes any number of views as a numpy array along with associated parameters as a dictionary.
        Returns a fit model object which can be used to predict correlations or transform out of sample data.
        :param views: 2D numpy arrays for each view with the same number of rows (nxp)
        :param c: regularisation between 0 (CCA) and 1 (PLS)
        :return: training data correlations and the parameters required to call other functions in the class.
        """
        self.c = c
        if self.c is None:
            self.c = [0] * len(views)
        assert (len(self.c) == len(views)), 'c requires as many values as #views'
        views_demeaned = self.demean_data(*views)
        all_views = np.concatenate(views_demeaned, axis=1)
        C = all_views.T @ all_views
        # Can regularise by adding to diagonal
        D = block_diag(*[(1 - self.c[i]) * m.T @ m + self.c[i] * np.eye(m.shape[1]) for i, m in
                         enumerate(views_demeaned)])
        C -= block_diag(*[m.T @ m for i, m in
                          enumerate(views_demeaned)]) - D
        [eigvals, eigvecs] = eigh(C, D)
        idx = np.argsort(eigvals, axis=0)[::-1]
        eigvecs = eigvecs[:, idx].real
        splits = np.cumsum([0] + [view.shape[1] for view in views])
        self.weights_list = [eigvecs[split:splits[i + 1], :self.latent_dims] for i, split in enumerate(splits[:-1])]
        self.score_list = [view @ self.weights_list[i] for i, view in enumerate(views_demeaned)]
        self.train_correlations = self.predict_corr(*views)
        return self

    def transform(self, *views):
        transformed_views = []
        for i, view in enumerate(views):
            transformed_views.append((view - self.view_means[i]) @ self.weights_list[i])
        return transformed_views


class GCCA(CCA_Base):
    def __init__(self, latent_dims: int = 1):
        super().__init__(latent_dims=latent_dims)

    def fit(self, *views, c=None, view_weights=None, K=None):
        """
        The fit method takes any number of views as a numpy array along with associated parameters as a dictionary.
        Returns a fit model object which can be used to predict correlations or transform out of sample data.
        :param views: 2D numpy arrays for each view with the same number of rows (nxp)
        :param c: regularisation between 0 (CCA) and 1 (PLS)
        :param view_weights: weights for each view as in Learning Multiview Embeddings of Twitter Users http://www.cs.jhu.edu/~mdredze/publications/2016_acl_multiview.pdf
        :param K: "row selection matrix" as in Multiview LSA: Representation Learning via Generalized CCA https://www.aclweb.org/anthology/N15-1058.pdf
            binary numpy array with dimensions (#views,#rows) with one for observed and zero for not observed for that view.
        :return: training data correlations and the parameters required to call other functions in the class.
        """
        self.c = c
        if self.c is None:
            self.c = [0] * len(views)
        assert (len(self.c) == len(views)), 'c requires as many values as #views'
        self.view_weights = view_weights
        if self.view_weights is None:
            self.view_weights = [1] * len(views)
        self.K = K
        if self.K is None:
            # just use identity when all rows are observed in all views.
            self.K = np.ones((len(views), views[0].shape[0]))
        views_demeaned = self.demean_observed_data(*views, self.K)
        Q = []
        for i, (view, view_weight) in enumerate(zip(views_demeaned, self.view_weights)):
            view_cov = view.T @ view
            view_cov = (1 - self.c[i]) * view_cov + self.c[i] * np.eye(view_cov.shape[0])
            Q.append(view_weight * view @ np.linalg.inv(view_cov) @ view.T)
        Q = np.sum(Q, axis=0)
        self.K = np.sqrt(np.sum(self.K, axis=0))
        Q = np.diag(self.K) @ Q @ np.diag(self.K)
        [eigvals, eigvecs] = np.linalg.eig(Q)
        idx = np.argsort(eigvals, axis=0)[::-1]
        eigvecs = eigvecs[:, idx].real
        eigvals = eigvals[idx].real
        self.weights_list = [np.linalg.pinv(view) @ eigvecs[:, :self.latent_dims] for view in views_demeaned]
        self.score_list = [view @ self.weights_list[i] for i, view in enumerate(views_demeaned)]
        self.train_correlations = self.predict_corr(*views)
        return self

    def transform(self, *views):
        transformed_views = []
        for i, view in enumerate(views):
            transformed_views.append((view - self.view_means[i]) @ self.weights_list[i])
        return transformed_views

    def demean_observed_data(self, *views):
        """
        Since most methods require zero-mean data, demean_data() is used to demean training data as well as to apply this
        demeaning transformation to out of sample data
        :param views:
        :return:
        """
        views_demeaned = []
        self.view_means = []
        for i, (observations, view) in enumerate(zip(self.K, views)):
            observed = np.where(observations == 1)[0]
            self.view_means.append(view[observed].mean(axis=0))
            view[observed] = view[observed] - self.view_means[i]
            views_demeaned.append(np.diag(observations) @ view)
        return views_demeaned


class Iterative(CCA_Base):
    def __init__(self, inner_loop: Type[cca_zoo.innerloop.InnerLoop] = cca_zoo.innerloop.InnerLoop,
                 latent_dims: int = 1, max_iter=100, deflation='cca'):
        super().__init__(latent_dims=latent_dims)
        self.inner_loop = inner_loop
        self.max_iter = max_iter

    def fit(self, *views, **kwargs):
        """
        Fits the model for a given set of parameters (or use default values). Returns parameters/objects that allow out of sample transformation or prediction
        :param views: numpy arrays separated by comma e.g. fit(view_1,view_2,view_3)
        :param kwargs: a dictionary containing the relevant parameters required for the model. If None use defaults.
        :return: training data correlations and the parameters required to call other functions in the class.
        """
        self.outer_loop(*self.demean_data(*views), **kwargs)
        self.train_correlations = self.predict_corr(*views)
        return self

    def transform(self, *views):
        transformed_views = []
        for i, view in enumerate(views):
            transformed_views.append((view - self.view_means[i]) @ self.weights_list[i])
        return transformed_views

    def outer_loop(self, *views, **kwargs):
        """
        :param views: numpy arrays separated by comma. Each view needs to have the same number of features as its
         corresponding view in the training data
        :return: complete set of weights and scores required to calcuate train correlations of latent dimensions and
         transformations of out of sample data
        """
        n = views[0].shape[0]
        p = [view.shape[1] for view in views]
        # list of d: p x k
        self.weights_list = [np.zeros((p_, self.latent_dims)) for p_ in p]

        # list of d: n x k
        self.score_list = [np.zeros((n, self.latent_dims)) for _ in views]

        residuals = copy.deepcopy(list(views))
        # For each of the dimensions
        for k in range(self.latent_dims):
            self.loop = self.inner_loop(*residuals, max_iter=self.max_iter, **kwargs)
            for i, residual in enumerate(residuals):
                self.weights_list[i][:, k] = self.loop.weights[i]
                self.score_list[i][:, k] = self.loop.scores[i]
                # TODO This is CCA deflation (https://ars.els-cdn.com/content/image/1-s2.0-S0006322319319183-mmc1.pdf)
                # but in principle we could apply any form of deflation here
                residuals[i] = residuals[i] - np.outer(self.score_list[i][:, k], self.score_list[i][:, k]) @ residuals[
                    i] / np.dot(self.score_list[i][:, k], self.score_list[i][:, k]).item()
        # can we fix the numerical instability problem?
        return self

    def deflate(self, view, residual, score):
        pass


class PLS(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits a partial least squares model with CCA deflation by NIPALS algorithm
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.PLSInnerLoop, latent_dims, max_iter)


class CCA(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits a CCA model with CCA deflation by NIPALS algorithm
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.CCAInnerLoop, latent_dims, max_iter)


class PMD(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits a sparse CCA model by penalized matrix decomposition
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.PMDInnerLoop, latent_dims, max_iter)


class ParkhomenkoCCA(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits a sparse CCA model by penalization
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.ParkhomenkoInnerLoop, latent_dims, max_iter)


class SCCA(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits a sparse CCA model by iterative rescaled lasso regression
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.SCCAInnerLoop, latent_dims, max_iter)


class SCCA_ADMM(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits a sparse CCA model by alternating ADMM
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.ADMMInnerLoop, latent_dims, max_iter)


class ElasticCCA(Iterative):
    def __init__(self, latent_dims: int = 1, max_iter=100):
        """
        Fits an elastic CCA by iterative rescaled elastic net regression
        :param latent_dims: Number of latent dimensions
        :param max_iter: Maximum number of iterations
        """
        super().__init__(cca_zoo.innerloop.ElasticInnerLoop, latent_dims, max_iter)


def slicedict(d, s):
    """
    :param d: dictionary containing e.g. c_1, c_2
    :param s:
    :return:
    """
    return {k: v for k, v in d.items() if k.startswith(s)}


class CrossValidate:
    def __init__(self, model: CCA_Base, folds: int = 5, verbose: bool = True):
        self.folds = folds
        self.verbose = verbose
        self.model = model

    def score(self, *views, **kwargs):
        scores = np.zeros(self.folds)
        inds = np.arange(views[0].shape[0])
        np.random.shuffle(inds)
        if self.folds == 1:
            # If 1 fold do an 80:20 split
            fold_inds = np.array_split(inds, 5)
        else:
            fold_inds = np.array_split(inds, self.folds)
        for fold in range(self.folds):
            train_sets = [np.delete(view, fold_inds[fold], axis=0) for view in views]
            val_sets = [view[fold_inds[fold], :] for view in views]
            scores[fold] = self.model.fit(
                *train_sets, **kwargs).predict_corr(
                *val_sets).sum(axis=-1)[np.triu_indices(len(views), 1)].sum()
        metric = scores.sum(axis=0) / self.folds
        std = scores.std(axis=0)
        if np.isnan(metric):
            metric = 0
        if self.verbose:
            print(kwargs)
            print(metric)
            print(std)
        return metric, std
