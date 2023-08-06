# -*- coding: utf-8 -*-

from __future__ import absolute_import

import numpy as np
import pandas as pd

from sklearn.utils import resample

from cell2cell.preprocessing import rnaseq, ppi


def generate_random_rnaseq(size, row_names, random_state=None, verbose=True):
    '''
    This function generates a RNA-seq datasets-set that is genes wise normally distributed, in TPM units (each column).
    All row values for a given columns sum up to 1 million.

    Parameters
    ----------
    size : int
        Number of samples (columns).

    row_names : array-like
        List containing the name of genes (rows).

    Returns
    -------
    df : pandas.DataFrame
        Dataframe containing gene expression given the list of genes for each sample.
    '''
    if verbose:
        print('Generating random RNA-seq dataset.')
    columns = ['Cell-{}'.format(c) for c in range(1, size+1)]

    if random_state is not None:
        np.random.seed(random_state)
    data = np.random.randn(len(row_names), len(columns))    # Normal distribution
    min = np.abs(np.amin(data, axis=1))
    min = min.reshape((len(min), 1))

    data = data + min
    df = pd.DataFrame(data, index=row_names, columns=columns)
    if verbose:
        print('Normalizing random RNA-seq dataset (into TPM)')
    df = rnaseq.scale_expression_by_sum(df, axis=0, sum_value=1e6)
    return df


def generate_random_ppi(max_size, interactors_A, interactors_B=None, random_state=None, verbose=True):
    if interactors_B is not None:
        assert max_size <= len(interactors_A)*len(interactors_B)
    else:
        assert max_size <= len(interactors_A)**2


    if verbose:
        print('Generating random PPI network.')

    def small_block_ppi(size, interactors_A, interactors_B, random_state):
        if random_state is not None:
            random_state += 1
        if interactors_B is None:
            interactors_B = interactors_A

        col_A = resample(interactors_A, n_samples=size, random_state=random_state)
        col_B = resample(interactors_B, n_samples=size, random_state=random_state)

        ppi_data = pd.DataFrame()
        ppi_data['A'] = col_A
        ppi_data['B'] = col_B
        ppi_data.assign(score=1.0)

        ppi_data = ppi.remove_ppi_bidirectionality(ppi_data, ('A', 'B'), verbose=verbose)
        ppi_data = ppi_data.drop_duplicates()
        ppi_data.reset_index(inplace=True, drop=True)
        return ppi_data

    ppi_data = small_block_ppi(max_size*2, interactors_A, interactors_B, random_state)

    # TODO: This part need to be fixed, it does not converge to the max_size -> len((set(A)) * len(set(B) - set(A)))
    # while ppi_data.shape[0] < size:
    #     if random_state is not None:
    #         random_state += 2
    #     b = small_block_ppi(size, interactors_A, interactors_B, random_state)
    #     print(b)
    #     ppi_data = pd.concat([ppi_data, b])
    #     ppi_data = ppi.remove_ppi_bidirectionality(ppi_data, ('A', 'B'), verbose=verbose)
    #     ppi_data = ppi_data.drop_duplicates()
    #     ppi_data.dropna()
    #     ppi_data.reset_index(inplace=True, drop=True)
    #     print(ppi_data.shape[0])

    if ppi_data.shape[0] > max_size:
        ppi_data = ppi_data.loc[list(range(max_size)), :]
    ppi_data.reset_index(inplace=True, drop=True)
    return ppi_data


def generate_random_cci_scores(cell_number, labels=None, random_state=None):
    if labels is not None:
        assert len(labels) == cell_number
    else:
        labels = ['Cell-{}'.format(n) for n in range(1, cell_number+1)]

    if random_state is not None:
        np.random.seed(random_state)
    cci_scores = np.random.random((cell_number, cell_number))
    cci_scores = (cci_scores + cci_scores.T) / 2
    cci_matrix = pd.DataFrame(cci_scores, index=labels, columns=labels)

    return cci_matrix


def generate_random_metadata(cell_labels, group_number):
    metadata = pd.DataFrame()
    metadata['Cell'] = cell_labels

    groups = list(range(1, group_number+1))
    metadata['Group'] = metadata['Cell'].apply(lambda x: np.random.choice(groups, 1)[0])
    return metadata
