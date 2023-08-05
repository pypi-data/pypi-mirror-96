#    A collection of tools to interface with manually traced and autosegmented
#    data in FAFB.
#
#    Copyright (C) 2019 Philipp Schlegel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import navis

import numpy as np
import pandas as pd

from .segmentation import roots_to_supervoxels, supervoxels_to_roots

from ..synapses.utils import catmaid_table
from ..synapses.transmitters import collapse_nt_predictions
from .. import spine

__all__ = ['fetch_synapses', 'fetch_connectivity', 'predict_transmitter']


def predict_transmitter(x, single_pred=False, dataset='production'):
    """Fetch neurotransmitter predictions for neurons.

    Based on Eckstein et al. (2020). Uses a service on spine.janelia.org hosted
    by Eric Perlman and Davi Bock. The per-synapse predictions are collapsed
    into per-neuron prediction by calculating the average confidence for
    each neurotransmitter across all synapses weighted by the "cleft score".
    Bottom line: higher confidence synapses have more weight than low confidence
    synapses.

    Parameters
    ----------
    x :             int | list of int | Neuron/List
                    Either a flywire segment ID (i.e. root ID), a list thereof or
                    a Neuron/List. For neurons, the ``.id`` is assumed to be the
                    root ID. If you have a neuron (in FlyWire space) but don't
                    know its ID, use :func:`fafbseg.flywire.neuron_to_segments`
                    first.
    single_pred :   bool
                    Whether to only return the highest probability transmitter
                    for each neuron.
    dataset :       str | CloudVolume
                    Against which flywire dataset to query::
                        - "production" (current production dataset, fly_v31)
                        - "sandbox" (i.e. fly_v26)

    Returns
    -------
    pandas.DataFrame
                    If `single_pred=False`: returns a dataframe with all
                    per-transmitter confidences for each query neuron.

    dict
                    If `single_pred=True`: returns dictionary with
                    `(top_transmitter, confidence)` tuple for each query neuron.

    """
    # First get the synapses
    syn = fetch_synapses(x, pre=True, post=False, attach=False, min_score=None,
                         transmitters=True)

    # Get the predictions
    return collapse_nt_predictions(syn, single_pred=single_pred, id_col='pre')


def fetch_synapses(x, pre=True, post=True, attach=True, min_score=0,
                   dataset='production', transmitters=False, progress=True):
    """Fetch Buhmann et al. (2019) synapses for given neuron(s).

    Uses a service on spine.janelia.org hosted by Eric Perlman and Davi Bock.

    Parameters
    ----------
    x :             int | list of int | Neuron/List
                    Either a flywire segment ID (i.e. root ID), a list thereof
                    or a Neuron/List. For neurons, the ``.id`` is assumed to be
                    the root ID. If you have a neuron (in FlyWire space) but
                    don't know its ID, use
                    :func:`fafbseg.flywire.neuron_to_segments` first.
    pre :           bool
                    Whether to fetch presynapses for the given neurons.
    post :          bool
                    Whether to fetch postsynapses for the given neurons.
    transmitters :  bool
                    Whether to also load neurotransmitter predictions from
                    Eckstein et al. (2020).
    attach :        bool
                    If True and ``x`` is Neuron/List, the synapses will be added
                    as ``.connectors`` table. For TreeNeurons (skeletons), the
                    synapses will be mapped to the closest node.
    dataset :       str | CloudVolume
                    Against which flywire dataset to query::
                        - "production" (current production dataset, fly_v31)
                        - "sandbox" (i.e. fly_v26)

    Returns
    -------
    pandas.DataFrame

    """
    if not pre and not post:
        raise ValueError('`pre` and `post` must not both be False')

    if isinstance(x, navis.BaseNeuron):
        ids = [x.id]
        x = navis.NeuronList(x)
    elif isinstance(x, navis.NeuronList):
        ids = x.id
    elif isinstance(x, (int, np.int)):
        ids = [x]
    else:
        ids = navis.utils.make_iterable(x)

    # Make sure we are working with proper numerical IDs
    try:
        ids = np.asarray(ids).astype(int)
    except ValueError:
        raise ValueError(f'Unable to convert IDs to integer: {ids}')
    except BaseException:
        raise

    # Now get supervoxels for these root IDs
    # (this is a dict)
    roots2svxl = roots_to_supervoxels(ids, dataset=dataset, progress=progress)
    # Turn dict into array of supervoxels
    svoxels = np.concatenate(list(roots2svxl.values()))

    # Query the synapses
    syn = spine.synapses.get_connectivity(svoxels,
                                          locations=True,
                                          nt_predictions=transmitters,
                                          segmentation='flywire_supervoxels')

    # Next we need to run some clean-up:
    # 1. Drop below threshold connections
    if min_score:
        syn = syn[syn.cleft_scores >= min_score]
    # 2. Drop connections involving 0 (background, glia)
    syn = syn[(syn.pre != 0) & (syn.post != 0)]

    # Avoid copy warning
    syn = syn.copy()

    # Now map the supervoxels to root IDs
    svoxels = np.unique(syn[['pre', 'post']].values.flatten())
    roots = supervoxels_to_roots(svoxels, dataset=dataset)

    dct = dict(zip(svoxels, roots))

    # Check if any of the query IDs are outdated in which case the newly
    # fetch supervoxels->root IDs map might not point to any of the query IDs
    # anymore: in that case we have to enforce the old root IDs
    outdated = [str(i) for i in ids if i not in roots]
    if any(outdated):
        dct.update({v: r for r in roots2svxl for v in roots2svxl[r]})

    syn['pre'] = syn.pre.map(dct)
    syn['post'] = syn.post.map(dct)

    if not pre:
        # Drop synapses where `post` is not in query IDs
        syn = syn[syn.post.isin(ids)].copy()
    if not post:
        # Drop synapses where `pre` is not in query IDs
        syn = syn[syn.pre.isin(ids)].copy()

    if attach and isinstance(x, navis.NeuronList):
        for n in x:
            if pre:
                pre = syn.loc[syn.pre == int(n.id),
                              ['pre_x', 'pre_y', 'pre_z',
                               'cleft_scores', 'post']].rename({'pre_x': 'x',
                                                                'pre_y': 'y',
                                                                'pre_z': 'z',
                                                                'post': 'partner_id'},
                                                               axis=1)
                pre['type'] = 'pre'
            if post:
                post = syn.loc[syn.post == int(n.id),
                               ['post_x', 'post_y', 'post_z',
                                'cleft_scores', 'pre']].rename({'post_x': 'x',
                                                                'post_y': 'y',
                                                                'post_z': 'z',
                                                                'pre': 'partner_id'},
                                                               axis=1)
                post['type'] = 'post'
            if isinstance(pre, pd.DataFrame) and isinstance(post, pd.DataFrame):
                connectors = pd.concat((pre, post), axis=0, ignore_index=True)
            elif isinstance(pre, pd.DataFrame):
                connectors = pre
            else:
                connectors = post

            # Turn type column into categorical to save memory
            connectors['type'] = connectors['type'].astype('category')

            # If TreeNeuron, map each synapse to a node
            if isinstance(n, navis.TreeNeuron):
                tree = navis.neuron2KDTree(n, data='nodes')
                dist, ix = tree.query(connectors[['x', 'y', 'z']].values)
                connectors['node_id'] = n.nodes.node_id.values[ix]

            n.connectors = connectors

    return syn


def fetch_connectivity(x, clean=True, style='catmaid', min_score=30,
                       transmitters=False, dataset='production', progress=True):
    """Fetch Buhmann et al. (2019) connectivity for given neuron(s).

    Uses a service on spine.janelia.org hosted by Eric Perlman and Davi Bock.

    Parameters
    ----------
    x :             int | list of int | Neuron/List
                    Either a flywire segment ID (i.e. root ID), a list thereof
                    or a Neuron/List. For neurons, the ``.id`` is assumed to be
                    the root ID. If you have a neuron (in FlyWire space) but
                    don't know its ID, use :func:`fafbseg.flywire.neuron_to_segments`
                    first.
    clean :         bool
                    If True, we will perform some clean up of the connectivity
                    compared with the raw synapse information. Currently, we::
                        - drop autapses
                        - drop synapses from/to background (id 0)

    style :             "simple" | "catmaid"
                    Style of the returned table.
    min_score :     int
                    Minimum "cleft score". The default of 30 is what Buhmann et al.
                    used in the paper.
    transmitter :   bool
                    If True, will attach the best guess for the transmitter
                    for a given connection based on the predictions in Eckstein
                    et al (2020). IMPORTANT: the predictions are based solely on
                    the connections retrieved as part of this query which likely
                    represent only a fraction of each neuron's total synapses.
                    As such the predictions need to be taken with a grain
                    of salt - in particular for weak connections!
                    To get the "full" predictions see
                    :func:`fafbseg.flywire.predict_transmitter`.
    dataset :       str | CloudVolume
                    Against which flywire dataset to query::
                        - "production" (current production dataset, fly_v31)
                        - "sandbox" (i.e. fly_v26)


    Returns
    -------
    pd.DataFrame
                Connectivity table.

    """
    if isinstance(x, navis.BaseNeuron):
        ids = [x.id]
    elif isinstance(x, navis.NeuronList):
        ids = x.id
    elif isinstance(x, (int, np.int)):
        ids = [x]
    else:
        ids = navis.utils.make_iterable(x)

    # Make sure we are working with proper numerical IDs
    try:
        ids = np.asarray(ids).astype(int)
    except ValueError:
        raise ValueError(f'Unable to convert IDs to integer: {ids}')
    except BaseException:
        raise

    if transmitters and style == 'catmaid':
        raise ValueError('`style` must be "simple" when asking for transmitters')

    # Now get supervoxels for these root IDs
    # (this is a dict)
    roots2svxl = roots_to_supervoxels(ids, dataset=dataset, progress=progress)
    # Turn dict into array of supervoxels
    svoxels = np.concatenate(list(roots2svxl.values()))

    # Query the synapses
    syn = spine.synapses.get_connectivity(svoxels,
                                          segmentation='flywire_supervoxels',
                                          nt_predictions=transmitters)

    # Next we need to run some clean-up:
    # 1. Drop below threshold connections
    if min_score:
        syn = syn[syn.cleft_scores >= min_score]
    # 2. Drop connections involving 0 (background, glia)
    syn = syn[(syn.pre != 0) & (syn.post != 0)]

    # Avoid copy warning
    syn = syn.copy()

    # Now map the supervoxels to root IDs
    svoxels = np.unique(syn[['pre', 'post']].values.flatten())
    roots = supervoxels_to_roots(svoxels, dataset=dataset)

    dct = dict(zip(svoxels, roots))

    # Check if any of the query IDs are outdated
    outdated = [i for i in ids if i not in roots]
    if any(outdated):
        print(f'Query ID(s) {", ".join(outdated)} are outdated and connectivity'
              ' might be inaccurrate.')
        dct.update({v: r for r in roots2svxl for v in roots2svxl[r]})

    syn['pre'] = syn.pre.map(dct)
    syn['post'] = syn.post.map(dct)

    # Turn into connectivity table
    cn_table = syn.groupby(['pre', 'post'], as_index=False).size().rename({'size': 'weight'}, axis=1)

    # Style
    if style == 'catmaid':
        cn_table = catmaid_table(cn_table, query_ids=ids)
    else:
        cn_table.sort_values('weight', ascending=False, inplace=True)

    if transmitters:
        # Generate per-neuron predictions
        pred = collapse_nt_predictions(syn, single_pred=True, id_col='pre')

        cn_table['pred_nt'] = cn_table.pre.map(lambda x: pred.get(x, [None])[0])
        cn_table['pred_conf'] = cn_table.pre.map(lambda x: pred.get(x, [None, None])[1])


    return cn_table
