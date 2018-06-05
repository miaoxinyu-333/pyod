# -*- coding: utf-8 -*-
"""
Utility functions for manipulating data
"""

from __future__ import division
from __future__ import print_function

import numpy as np
from sklearn.utils import check_X_y
from sklearn.utils import column_or_1d
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from pyod.utils.utility import precision_n_scores


def generate_data(n_train=1000, n_test=500, contamination=0.1,
                  train_only=False):
    """
    Utility function to generate synthesized data
    normal data is generated by a 2-d Gaussian distribution
    outliers are generated by a 2-d uniform distribution

    :param train_only: generate train data only
    :type train_only: bool, optional(default=False)

    :param n_train: number of training points to generate
    :type n_train: int, (default=1000)

    :param n_test: number of test points to generate
    :type n_test: int

    :param contamination: The amount of contamination of the data set,
        i.e. the proportion of outliers in the data set. Used when fitting to
        define the threshold on the decision function.
    :type contamination: float in (0., 0.5), optional (default=0.1)

    :return: training data and test data (c_train and c_test are colors)
    :rtype: tuple, (ndarry, ndarry, list, ndarry, ndarry, list)
    """
    n_outliers = int(n_train * contamination)
    n_inliers = int(n_train - n_outliers)

    n_outliers_test = int(n_test * contamination)
    n_inliers_test = int(n_test - n_outliers_test)

    offset = 2

    # generate inliers
    X1 = 0.3 * np.random.randn(n_inliers // 2, 2) - offset
    X2 = 0.3 * np.random.randn(n_inliers // 2, 2) + offset
    X_train = np.r_[X1, X2]

    # generate outliers
    X_train = np.r_[
        X_train, np.random.uniform(low=-6, high=6, size=(n_outliers, 2))]

    # generate target
    y_train = np.zeros([X_train.shape[0], 1])
    # c_train = np.full([X_train.shape[0]], 'b', dtype=str)
    y_train[n_inliers:, ] = 1
    # c_train[n_inliers:, ] = 'r'
    X_train, y_train = check_X_y(X_train, y_train.ravel())

    if train_only:
        # return X_train, y_train, c_train
        return X_train, y_train

    # generate test data
    X1_test = 0.3 * np.random.randn(n_inliers_test // 2, 2) - offset
    X2_test = 0.3 * np.random.randn(n_inliers_test // 2, 2) + offset
    X_test = np.r_[X1_test, X2_test]

    # generate outliers
    X_test = np.r_[
        X_test, np.random.uniform(low=-8, high=8, size=(n_outliers_test, 2))]
    y_test = np.zeros([X_test.shape[0], 1])

    # c_test = np.full([X_test.shape[0]], 'b', dtype=str)

    y_test[n_inliers_test:] = 1
    # c_test[n_inliers_test:] = 'r'
    X_test, y_test = check_X_y(X_test, y_test.ravel())

    # return X_train, y_train, c_train, X_test, y_test, c_test
    return X_train, y_train, X_test, y_test


def _get_color_codes(y):
    """
    Internal function to generate color codes for inliers and outliers
    Inliers (0): blue
    Outlier (1): red

    :param y: The binary labels of the groud truth, where 0 is inlier
    :type y: list, array, numpy array of shape (n_samples,)

    :return: The list of color codes ['r', 'b', ..., 'b']
    :rtype: list
    """
    y = column_or_1d(y)

    # inliers are assigned blue
    c = np.full([len(y)], 'b', dtype=str)
    outliers_ind = np.where(y == 1)

    # outlier are assigned red
    c[outliers_ind] = 'r'

    return c


def visualize(clf_name, X_train, y_train, X_test, y_test, y_train_pred,
              y_test_pred, show_figure=True, save_figure=False):
    """
    Utility function for visualizing the results in examples
    Internal use only

    :param clf_name: The name of the detector
    :type clf_name: str

    :param X_train: The training samples
    :param X_train: numpy array of shape (n_samples, n_features)

    :param y_train: The ground truth of training samples
    :type y_train: list or array of shape (n_samples,)

    :param X_test: The test samples
    :type X_test: numpy array of shape (n_samples, n_features)

    :param y_test: The ground truth of test samples
    :type y_test: list or array of shape (n_samples,)

    :param y_train_pred: The predicted outlier scores on the training samples
    :type y_train_pred: numpy array of shape (n_samples, n_features)

    :param y_test_pred: The predicted outlier scores on the test samples
    :type y_test_pred: numpy array of shape (n_samples, n_features)

    :param show_figure: If set to True, show the figure
    :type show_figure: bool, optional (default=True)

    :param save_figure: If set to True, save the figure to the local
    :type save_figure: bool, optional (default=False)
    """

    c_train = _get_color_codes(y_train)
    c_test = _get_color_codes(y_test)

    fig = plt.figure(figsize=(12, 10))
    plt.suptitle("Demo of {clf_name}".format(clf_name=clf_name))

    fig.add_subplot(221)
    plt.scatter(X_train[:, 0], X_train[:, 1], c=c_train)
    plt.title('Train ground truth')
    legend_elements = [Line2D([0], [0], marker='o', color='w', label='normal',
                              markerfacecolor='b', markersize=8),
                       Line2D([0], [0], marker='o', color='w', label='outlier',
                              markerfacecolor='r', markersize=8)]

    plt.legend(handles=legend_elements, loc=4)

    fig.add_subplot(222)
    plt.scatter(X_test[:, 0], X_test[:, 1], c=c_test)
    plt.title('Test ground truth')
    plt.legend(handles=legend_elements, loc=4)

    fig.add_subplot(223)
    plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train_pred)
    plt.title('Train prediction by {clf_name}'.format(clf_name=clf_name))
    legend_elements = [Line2D([0], [0], marker='o', color='w', label='normal',
                              markerfacecolor='0', markersize=8),
                       Line2D([0], [0], marker='o', color='w', label='outlier',
                              markerfacecolor='yellow', markersize=8)]
    plt.legend(handles=legend_elements, loc=4)

    fig.add_subplot(224)
    plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test_pred)
    plt.title('Test prediction by {clf_name}'.format(clf_name=clf_name))
    plt.legend(handles=legend_elements, loc=4)

    if save_figure:
        plt.savefig('{clf_name}.png'.format(clf_name=clf_name), dpi=300)
    if show_figure:
        plt.show()
    return


def evaluate_print(clf_name, y, y_pred):
    """
    Utility function for evaluating and printing the results for examples
    Internal use only

    :param clf_name: The name of the detector
    :type clf_name: str

    :param y: The ground truth
    :type y: list or array of shape (n_samples,)

    :param y_pred: The predicted outlier scores
    :type y: list or array of shape (n_samples,)
    """
    y = column_or_1d(y)
    y_pred = column_or_1d(y_pred)

    print('{clf_name} ROC:{roc}, precision @ rank n:{prn}'.format(
        clf_name=clf_name,
        roc=np.round(roc_auc_score(y, y_pred), decimals=4),
        prn=np.round(precision_n_scores(y, y_pred), decimals=4)))
