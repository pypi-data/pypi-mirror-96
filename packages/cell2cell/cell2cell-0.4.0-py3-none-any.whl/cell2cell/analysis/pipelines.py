# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

import cell2cell.plotting.ccc_plot
import cell2cell.plotting.cci_plot
import cell2cell.plotting.pcoa_plot
from cell2cell.core import interaction_space as ispace
from cell2cell.datasets import heuristic_data
from cell2cell.io import read_data
from cell2cell.preprocessing import gene_ontology, integrate_data, ppi


def basic_pipeline(rnaseq_data, ppi_data, cutoff_setup, analysis_setup, excluded_cells=None,
                   use_ppi_score=False,verbose=True):

    if excluded_cells is None:
        excluded_cells = []

    if analysis_setup['cci_type'] == 'undirected':
        bi_ppi_data = ppi.bidirectional_ppi_for_cci(ppi_data=ppi_data, verbose=False)
    else:
        bi_ppi_data = ppi_data.copy()


    included_cells = sorted(list((set(rnaseq_data.columns) - set(excluded_cells))))

    interaction_space = ispace.InteractionSpace(rnaseq_data=rnaseq_data[included_cells],
                                                ppi_data=bi_ppi_data,
                                                gene_cutoffs=cutoff_setup,
                                                communication_score=analysis_setup['communication_score'],
                                                cci_score=analysis_setup['cci_score'],
                                                cci_type=analysis_setup['cci_type'],
                                                verbose=verbose)

    interaction_space.compute_pairwise_cci_scores(use_ppi_score=use_ppi_score,
                                                  verbose=verbose)

    return interaction_space


def core_pipeline(files, rnaseq_data, ppi_data, metadata, meta_setup, cutoff_setup, analysis_setup, excluded_cells=None,
                  use_ppi_score=False, make_plots=True, colors=None, ccc_clustermap_metric='jaccard', filename_suffix='',
                  verbose=True):

    if excluded_cells is None:
        excluded_cells = []

    # Generate reference ppi data for generating directed CCC clustermap later
    if analysis_setup['cci_type'] == 'undirected':
        ref_ppi = ppi_data
    else:
        ref_ppi = None

    # Generate interaction space and compute parwise CCI scores
    interaction_space = basic_pipeline(rnaseq_data=rnaseq_data,
                                       ppi_data=ppi_data,
                                       cutoff_setup=cutoff_setup,
                                       analysis_setup=analysis_setup,
                                       excluded_cells=excluded_cells,
                                       use_ppi_score=use_ppi_score,
                                       verbose=verbose)

    # Compute communication scores for each protein-protein interaction
    interaction_space.compute_pairwise_communication_scores(ref_ppi_data=ref_ppi,
                                                            use_ppi_score=use_ppi_score,
                                                            verbose=verbose)

    # Plots section
    if make_plots:
        clustermap = cell2cell.plotting.cci_plot.clustermap_cci(interaction_space,
                                                                method='ward',
                                                                excluded_cells=excluded_cells,
                                                                metadata=metadata,
                                                                sample_col=meta_setup['sample_col'],
                                                                group_col=meta_setup['group_col'],
                                                                colors=colors,
                                                                title='CCI scores for cell pairs',
                                                                filename=files['output_folder'] + 'CCI-Clustermap-CCI-scores{}.png'.format(filename_suffix),
                                                                **{'cmap': 'Blues'}
                                                                )

        # Run PCoA only if CCI matrix is symmetric
        pcoa_state = False
        if (interaction_space.interaction_elements['cci_matrix'].values.transpose() == interaction_space.interaction_elements['cci_matrix'].values).all():
            pcoa = cell2cell.plotting.pcoa_plot.pcoa_3dplot(interaction_space,
                                                            excluded_cells=excluded_cells,
                                                            metadata=metadata,
                                                            sample_col=meta_setup['sample_col'],
                                                            group_col=meta_setup['group_col'],
                                                            colors=colors,
                                                            title='PCoA for cells given their CCI scores',
                                                            filename=files['output_folder'] + 'CCI-PCoA-CCI-scores{}.png'.format(filename_suffix),
                                                            )
            pcoa_state = True

        interaction_clustermap = cell2cell.plotting.ccc_plot.clustermap_ccc(interaction_space,
                                                                            metric=ccc_clustermap_metric,
                                                                            metadata=metadata,
                                                                            sample_col=meta_setup['sample_col'],
                                                                            group_col=meta_setup['group_col'],
                                                                            colors=colors,
                                                                            excluded_cells=excluded_cells,
                                                                            title='Active ligand-receptor pairs for interacting cells',
                                                                            filename=files['output_folder'] + 'CCI-Active-LR-pairs{}.png'.format(filename_suffix),
                                                                            **{'figsize': (20, 40)}
                                                                            )

        interaction_clustermap.data2d.to_csv(files['output_folder'] + 'CCI-Active-LR-pairs{}.csv'.format(filename_suffix))

    # Save results
    outputs = dict()
    outputs['interaction_space'] = interaction_space
    if make_plots:
        outputs['cci_clustermap'] = clustermap
        if pcoa_state:
            outputs['pcoa'] = pcoa
        else:
            outputs['pcoa'] = None
        outputs['ccc_clustermap'] = interaction_clustermap
        outputs['LR-pairs'] = interaction_clustermap.data2d
    else:
        outputs['cci_clustermap'] = None
        outputs['pcoa'] = None
        outputs['ccc_clustermap'] = None
        outputs['LR-pairs'] = None
    return outputs


def ligand_receptor_pipeline(files, rnaseq_setup, ppi_setup, meta_setup, cutoff_setup, analysis_setup, excluded_cells=None,
                             colors=None,  use_ppi_score=False, filename_suffix='', verbose=True):
    if excluded_cells is None:
        excluded_cells = []

    # Check for output directory
    if 'output_folder' in files.keys():
        if not os.path.exists(files['output_folder']):
            os.makedirs(files['output_folder'])

    # Load Data
    rnaseq_data = read_data.load_rnaseq(rnaseq_file=files['rnaseq'],
                                        gene_column=rnaseq_setup['gene_col'],
                                        drop_nangenes=rnaseq_setup['drop_nangenes'],
                                        log_transformation=rnaseq_setup['log_transform'],
                                        format='auto',
                                        verbose=verbose)

    ppi_data = read_data.load_ppi(ppi_file=files['ppi'],
                                  interaction_columns=ppi_setup['protein_cols'],
                                  rnaseq_genes=list(rnaseq_data.index),
                                  format='auto',
                                  verbose=verbose)

    meta = read_data.load_metadata(metadata_file=files['metadata'],
                                   rnaseq_data=rnaseq_data,
                                   sample_col=meta_setup['sample_col'],
                                   format='auto',
                                   verbose=verbose)

    # Run Analysis
    outputs = core_pipeline(files=files,
                            rnaseq_data=rnaseq_data,
                            ppi_data=ppi_data,
                            metadata=meta,
                            meta_setup=meta_setup,
                            cutoff_setup=cutoff_setup,
                            analysis_setup=analysis_setup,
                            excluded_cells=excluded_cells,
                            colors=colors,
                            use_ppi_score=use_ppi_score,
                            filename_suffix=filename_suffix,
                            verbose=verbose)
    return outputs


def heuristic_pipeline(files, rnaseq_setup, ppi_setup, meta_setup, cutoff_setup, go_setup, analysis_setup,
                       contact_go_terms = None, mediator_go_terms = None, interaction_type='mediated',
                       excluded_cells=None, colors=None,  use_ppi_score=False, filename_suffix='', verbose=None):
    '''
    This function performs the analysis with the default list of GO terms to filter the proteins in the PPI network.

    Parameters
    ----------
    files : dict
        This dictionary contains the locations of files to use in the analysis. Use the following keys:
        'rnaseq' : location of RNAseq matrix for cell types.
        'ppi' : location of PPI network to use.
        'go_annotation' : location of go annotation file, usually obtained from http://current.geneontology.org/products/pages/downloads.html
        'go_terms' : location of .obo file which contains the hierarchy for Gene Ontology.
        'output_folder' : location of the folder where the outputs will be generated.

    rnaseq_setup : dict
        This dictionary contains the parameters to load a RNAseq expression matrix. Use the following keys:
        'gene_col' : column name were the gene names are provided.
        'drop_nangenes' : Boolean value to indicate whether to remove genes without expression values in all cells.
        'log_transform' : Boolean value to indicate whether to log transform the expression values.

    ppi_setup : dict
        This dictionary contains the parameters to load a PPI network. Use the following keys:
        'protein_cols' : A list with column names where interactors A & B are contained.

    cutoff_setup : dict
         This dictionary contains the parameters use cutoffs to make gene expression values be binary. Use the following keys:
         'type' : Type of cutoff to use (e.g. local_percentile or global_percentile)
         'parameter' : Parameter associated to the type of cutoff. If type is percentile, it should be the percentile value (e.g. 0.75).

    analysis_setup : dict


    contact_go_terms : list, None by default


    mediator_go_terms : list, None by default


    Returns
    -------
    subsampling_space : cell2cell.core.SpatialCCI


    ppi_dict : dict


    '''
    if excluded_cells is None:
        excluded_cells = []

    # Check for output directory
    if 'output_folder' in files.keys():
        if not os.path.exists(files['output_folder']):
            os.makedirs(files['output_folder'])

    # Load Data
    rnaseq_data = read_data.load_rnaseq(rnaseq_file=files['rnaseq'],
                                        gene_column=rnaseq_setup['gene_col'],
                                        drop_nangenes=rnaseq_setup['drop_nangenes'],
                                        log_transformation=rnaseq_setup['log_transform'],
                                        format='auto',
                                        verbose=verbose
                                        )

    meta = read_data.load_metadata(metadata_file=files['metadata'],
                                   rnaseq_data=rnaseq_data,
                                   sample_col=meta_setup['sample_col'],
                                   format='auto',
                                   verbose=verbose
                                   )

    ppi_data = read_data.load_ppi(ppi_file=files['ppi'],
                                  interaction_columns=ppi_setup['protein_cols'],
                                  rnaseq_genes=list(rnaseq_data.index),
                                  format='auto',
                                  verbose=verbose
                                  )

    go_annotations = read_data.load_go_annotations(goa_file=files['go_annotations'],
                                                   experimental_evidence=go_setup['experimental_evidence'],
                                                   verbose=verbose)

    go_terms = read_data.load_go_terms(go_terms_file=files['go_terms'],
                                       verbose=verbose)

    # Filter genes associated to GO terms
    default_heuristic_go = heuristic_data.HeuristicGOTerms()

    if contact_go_terms is None:
        contact_go_terms = default_heuristic_go.contact_go_terms

    if mediator_go_terms is None:
        mediator_go_terms = default_heuristic_go.mediator_go_terms

    contact_genes = gene_ontology.get_genes_from_go_hierarchy(go_annotations,
                                                              go_terms,
                                                              contact_go_terms,
                                                              verbose=verbose)

    mediator_genes = gene_ontology.get_genes_from_go_hierarchy(go_annotations,
                                                               go_terms,
                                                               mediator_go_terms,
                                                               verbose=verbose)

    contact_genes = list(set(contact_genes))
    mediator_genes = list(set(mediator_genes))

    # Run analysis
    ppi_dict = integrate_data.get_ppi_dict_from_proteins(ppi_data,
                                                         contact_genes,
                                                         mediator_genes,
                                                         bidirectional=False,
                                                         verbose=verbose
                                                         )


    outputs = core_pipeline(files=files,
                            rnaseq_data=rnaseq_data,
                            ppi_data=ppi_dict[interaction_type],
                            metadata=meta,
                            meta_setup=meta_setup,
                            cutoff_setup=cutoff_setup,
                            analysis_setup=analysis_setup,
                            excluded_cells=excluded_cells,
                            colors=colors,
                            use_ppi_score=use_ppi_score,
                            filename_suffix=filename_suffix,
                            verbose=verbose)
    return outputs