# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import tensorly as tl

from tqdm.auto import tqdm
from collections import OrderedDict

from cell2cell.core.communication_scores import compute_ccc_matrix
from cell2cell.preprocessing.ppi import get_genes_from_complexes
from cell2cell.preprocessing.rnaseq import add_complexes_to_expression
from cell2cell.preprocessing.ppi import filter_ppi_by_proteins
from cell2cell.tensor.factorization import _compute_tensor_factorization, _run_elbow_analysis, multiple_runs_elbow_analysis
from cell2cell.plotting.tensor_factors_plot import plot_elbow, plot_multiple_run_elbow


class BaseTensor():
    def __init__(self):
        # Save variables for this class
        self.communication_score = None
        self.how = None
        self.tensor = None
        self.genes = None
        self.cells = None
        self.order_names = [None, None, None, None]
        self.tl_object = None
        self.factors = None
        self.rank = None
        self.mask = None

    def compute_tensor_factorization(self, rank, tf_type='non_negative_cp', init='svd', random_state=None, verbose=False,
                                     **kwargs):
        tf = _compute_tensor_factorization(tensor=self.tensor,
                                           rank=rank,
                                           tf_type=tf_type,
                                           init=init,
                                           random_state=random_state,
                                           mask=self.mask,
                                           verbose=verbose,
                                           **kwargs)

        self.tl_object = tf
        factor_names = ['Factor {}'.format(i) for i in range(1, rank+1)]
        order_names = ['Context', 'LRs', 'Sender', 'Receiver']
        self.factors = OrderedDict(zip(order_names,
                                       [pd.DataFrame(f, index=idx, columns=factor_names) for f, idx in zip(tf.factors, self.order_names)]))
        self.rank = rank


    def elbow_rank_selection(self, upper_rank=50, runs=1, tf_type='non_negative_cp', init='svd', random_state=None, mask=None,
                             figsize=(4, 2.25), fontsize=14, filename=None, verbose=False, **kwargs):
        # Run analysis
        if verbose:
            print('Running Elbow Analysis')

        if runs == 1:
            loss = _run_elbow_analysis(tensor=self.tensor,
                                       upper_rank=upper_rank,
                                       tf_type=tf_type,
                                       init=init,
                                       random_state=random_state,
                                       mask=mask,
                                       verbose=verbose,
                                       **kwargs
                                       )

            fig = plot_elbow(loss=loss,
                             figsize=figsize,
                             fontsize=fontsize,
                             filename=filename)
        elif runs > 1:

            all_loss = multiple_runs_elbow_analysis(tensor=self.tensor,
                                                    upper_rank=upper_rank,
                                                    runs=runs,
                                                    tf_type=tf_type,
                                                    init=init,
                                                    random_state=random_state,
                                                    mask=mask,
                                                    verbose=verbose,
                                                    **kwargs
                                                    )

            fig = plot_multiple_run_elbow(all_loss=all_loss,
                                          figsize=figsize,
                                          fontsize=fontsize,
                                          filename=filename)

            # Same outputs as runs = 1
            loss = np.nanmean(all_loss, axis=0).tolist()
            loss = [(i+1, l) for i, l in enumerate(loss)]
        else:
            assert runs > 0, "Input runs must be an integer greater than 0"
        return fig, loss


    def get_top_factor_elements(self, order_name, factor_name, top_number=10):
        top_elements = self.factors[order_name][factor_name].sort_values(ascending=False).head(top_number)
        return top_elements


class InteractionTensor(BaseTensor):

    def __init__(self, rnaseq_matrices, ppi_data, context_names=None, how='inner', communication_score='expression_product',
                 complex_sep=None, upper_letter_comparison=True, interaction_columns=('A', 'B'), verbose=True):
        # Init BaseTensor
        BaseTensor.__init__(self)

        # Generate expression values for protein complexes in PPI data
        if complex_sep is not None:
            if verbose:
                print('Getting expression values for protein complexes')
            col_a_genes, complex_a, col_b_genes, complex_b, complexes = get_genes_from_complexes(ppi_data=ppi_data,
                                                                                                 complex_sep=complex_sep,
                                                                                                 interaction_columns=interaction_columns
                                                                                                 )
            mod_rnaseq_matrices = [add_complexes_to_expression(rnaseq, complexes) for rnaseq in rnaseq_matrices]
        else:
            mod_rnaseq_matrices = [df.copy() for df in rnaseq_matrices]

        # Uppercase for Gene names
        if upper_letter_comparison:
            for df in mod_rnaseq_matrices:
                df.index = [idx.upper() for idx in df.index]


        # Get context CCC tensor
        tensor, genes, cells, ppi_names, mask = build_context_ccc_tensor(rnaseq_matrices=mod_rnaseq_matrices,
                                                                         ppi_data=ppi_data,
                                                                         how=how,
                                                                         communication_score=communication_score,
                                                                         complex_sep=complex_sep,
                                                                         upper_letter_comparison=upper_letter_comparison,
                                                                         interaction_columns=interaction_columns,
                                                                         verbose=verbose)

        # Generate names for the elements in each dimension (order) in the tensor
        if context_names is None:
            context_names = ['C-' + str(i) for i in range(1, len(mod_rnaseq_matrices)+1)]
            # for PPIS use ppis, and sender & receiver cells, use cells

        # Save variables for this class
        self.communication_score = communication_score
        self.how = how
        self.tensor = tl.tensor(tensor)
        self.genes = genes
        self.cells = cells
        self.order_names = [context_names, ppi_names, self.cells, self.cells]
        self.mask = mask


def build_context_ccc_tensor(rnaseq_matrices, ppi_data, how='inner', communication_score='expression_product',
                             complex_sep=None, upper_letter_comparison=True, interaction_columns=('A', 'B'), verbose=True):

    df_idxs = [list(rnaseq.index) for rnaseq in rnaseq_matrices]
    df_cols = [list(rnaseq.columns) for rnaseq in rnaseq_matrices]
    if how == 'inner':
        genes = set.intersection(*map(set, df_idxs))
        cells = set.intersection(*map(set, df_cols))
    elif how == 'outer':
        genes = set.union(*map(set, df_idxs))
        cells = set.union(*map(set, df_cols))
    else:
        raise ValueError('Provide a valid way to build the tensor; "how" must be "inner" or "outer" ')

    # Preserve order or sort new set (either inner or outer)
    if set(df_idxs[0]) == genes:
        genes = df_idxs[0]
    else:
        genes = sorted(list(genes))

    if set(df_cols[0]) == cells:
        cells = df_cols[0]
    else:
        cells = sorted(list(cells))

    # Filter PPI data for
    ppi_data_ = filter_ppi_by_proteins(ppi_data=ppi_data,
                                       proteins=genes,
                                       complex_sep=complex_sep,
                                       upper_letter_comparison=upper_letter_comparison,
                                       interaction_columns=interaction_columns)

    if verbose:
        print('Building tensor for the provided context')

    tensors = [generate_ccc_tensor(rnaseq_data=rnaseq.reindex(genes, fill_value=0.).reindex(cells, axis='columns', fill_value=0.),
                                   ppi_data=ppi_data_,
                                   communication_score=communication_score,
                                   interaction_columns=interaction_columns) for rnaseq in rnaseq_matrices]

    # Generate mask:
    if how == 'outer':
        mask_tensor = []
        for rnaseq in rnaseq_matrices:
            rna_cells = list(rnaseq.columns)
            ppi_mask = pd.DataFrame(np.ones((len(rna_cells), len(rna_cells))), columns=rna_cells, index=rna_cells)
            ppi_mask = ppi_mask.reindex(cells, fill_value=0.).reindex(cells, axis='columns', fill_value=0.) # Here we mask those cells that are not in the rnaseq data
            rna_tensor = [ppi_mask.values for i in range(ppi_data_.shape[0])] # Replicate the mask across all PPIs in ppi_data_
            mask_tensor.append(rna_tensor)
        mask_tensor = np.asarray(mask_tensor)
    else:
        mask_tensor = None

    ppi_names = [row[interaction_columns[0]] + '^' + row[interaction_columns[1]] for idx, row in ppi_data_.iterrows()]
    return tensors, genes, cells, ppi_names, mask_tensor


def generate_ccc_tensor(rnaseq_data, ppi_data, communication_score='expression_product', interaction_columns=('A', 'B')):
    ppi_a = interaction_columns[0]
    ppi_b = interaction_columns[1]

    ccc_tensor = []
    for idx, ppi in ppi_data.iterrows():
        v = rnaseq_data.loc[ppi[ppi_a], :].values
        w = rnaseq_data.loc[ppi[ppi_b], :].values
        ccc_tensor.append(compute_ccc_matrix(prot_a_exp=v,
                                             prot_b_exp=w,
                                             communication_score=communication_score).tolist())
    return ccc_tensor



