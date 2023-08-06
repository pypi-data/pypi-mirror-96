# -*- coding: utf-8 -*-

from __future__ import absolute_import

import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as hc
import scipy.spatial as sp


# Distance-based algorithms
def compute_distance(data_matrix, axis=0, metric='euclidean'):
    if (type(data_matrix) is pd.core.frame.DataFrame):
        data = data_matrix.values
    else:
        data = data_matrix
    if axis == 0:
        D = sp.distance.squareform(sp.distance.pdist(data, metric=metric))
    elif axis == 1:
        D = sp.distance.squareform(sp.distance.pdist(data.T, metric=metric))
    else:
        raise ValueError('Not valid axis. Use 0 or 1.')
    return D


def compute_linkage(distance_matrix, method='ward', optimal_ordering=True):
    '''
    This function returns a linkage for a given distance matrix using a specific method.

    Parameters
    ----------
    distance_matrix : numpy.ndarray
        A square array containing the distance between a given row and a given column. Diagonal cells must be zero.

    method : str, 'ward' by default
        Method to compute the linkage. It could be:
        'single'
        'complete'
        'average'
        'weighted'
        'centroid'
        'median'
        'ward'
        For more details, go to: https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.cluster.hierarchy.linkage.html

    Returns
    -------
    Z : numpy.ndarray
        The hierarchical clustering encoded as a linkage matrix.
    '''
    if (type(distance_matrix) is pd.core.frame.DataFrame):
        data = distance_matrix.values
    else:
        data = distance_matrix.copy()
    if ~(data.transpose() == data).all():
        raise ValueError('The matrix is not symmetric')

    np.fill_diagonal(data, 0.0)

    # Compute linkage
    D = sp.distance.squareform(data)
    Z = hc.linkage(D, method=method, optimal_ordering=optimal_ordering)
    return Z


def get_clusters_from_linkage(linkage, threshold, criterion='maxclust', labels=None):
    '''
    This function gets clusters from a linkage given a threshold and a criterion.

    Parameters
    ----------
    linkage : numpy.ndarray
        The hierarchical clustering encoded with the matrix returned by the linkage function (Z).

    threshold : float
        The threshold to apply when forming flat clusters.

    criterion : str, 'maxclust' by default
        The criterion to use in forming flat clusters. Depending on the criteron, the threshold has different meanings.
        More information on: https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.cluster.hierarchy.fcluster.html

    labels : array-like, None by default
        List of labels of the elements contained in the linkage. The order must match the order they were provided when
        generating the linkage.

    Returns
    -------
    clusters : dict
        A dictionary containing the clusters obtained. The keys correspond to the cluster numbers and the vaues to a list
        with element names given the labels, or the element index based on the linkage.
    '''

    cluster_ids = hc.fcluster(linkage, threshold, criterion=criterion)
    clusters = dict()
    for c in np.unique(cluster_ids):
        clusters[c] = []

    for i, c in enumerate(cluster_ids):
        if labels is not None:
            clusters[c].append(labels[i])
        else:
            clusters[c].append(i)
    return clusters