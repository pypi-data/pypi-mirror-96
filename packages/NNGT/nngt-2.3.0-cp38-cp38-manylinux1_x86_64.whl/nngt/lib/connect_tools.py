#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Generation tools for NNGT """

import logging

import numpy as np
import scipy.sparse as ssp
from scipy.spatial.distance import cdist
from numpy.random import randint

import nngt
from nngt.lib import InvalidArgument, nonstring_container
from nngt.lib.logger import _log_message


logger = logging.getLogger(__name__)


__all__ = [
    "_check_num_edges",
    "_compute_connections",
    "_filter",
    "_no_self_loops",
    "_set_degree_type",
    "_set_options",
    "_unique_rows",
    "dist_rule",
    "max_proba_dist_rule"
]


def _set_options(graph, population, shape, positions):
    ''' Make a graph a network or spatial '''
    if population is not None:
        nngt.Graph.make_network(graph, population)
    if shape is not None or positions is not None:
        nngt.Graph.make_spatial(graph, shape, positions)


def _compute_connections(num_source, num_target, density, edges, avg_deg,
                         directed, reciprocity=-1):
    assert (density, edges, avg_deg) != (None, None, None), \
        "At leat one of the following entries must be specified: 'density', " \
        "'edges', 'avg_deg'."

    pre_recip_edges = 0

    if avg_deg is not None:
        pre_recip_edges = int(avg_deg * num_source)
    elif edges is not None:
        pre_recip_edges = int(edges)
    else:
        pre_recip_edges = int(density * num_source * num_target)

    dens  = pre_recip_edges / float(num_source * num_target)
    edges = pre_recip_edges

    if edges:
        if reciprocity > max(0,(2.-1./dens)):
            frac_recip = ((reciprocity - 1.
                           + np.sqrt(1. + dens*(reciprocity - 2.))) /
                             (2. - reciprocity))
            if frac_recip < 1.:
                pre_recip_edges = int(edges/(1+frac_recip))
            else:
                raise InvalidArgument(
                    "Such reciprocity cannot be obtained, request ignored.")
        elif reciprocity > 0.:
            raise InvalidArgument(
                "Reciprocity cannot be lower than 2-1/density.")

    return edges, pre_recip_edges


def _check_num_edges(source_ids, target_ids, num_edges, directed, multigraph,
                     return_sets=False):
    num_source, num_target = len(source_ids), len(target_ids)

    source_set, target_set = None, None

    has_only_one_population = (num_source == num_target)

    if has_only_one_population:
        source_set = set(source_ids)
        target_set = set(target_ids)
        has_only_one_population = (source_set == target_set)

    if not has_only_one_population and not multigraph:
        b_d  = (num_edges > num_source*num_target)
        b_nd = (num_edges > int(0.5*num_source*num_target))

        if (not directed and b_nd) or (directed and b_d):
            raise InvalidArgument("Required number of edges is too high")
    elif has_only_one_population and not multigraph:
        b_d = (num_edges > num_source*(num_target-1))
        b_nd = (num_edges > int(0.5*(num_source-1)*num_target))

        if (not directed and b_nd) or (directed and b_d):
            raise InvalidArgument("Required number of edges is too high")

    if return_sets:
        return has_only_one_population, source_set, target_set

    return has_only_one_population


def _set_degree_type(degree_type):
    deg_map = {
        "in-degree": "in", "out-degree": "out", "total-degree": "total",
        "in": "in", "out": "out", "total": "total"
    }

    try:
        degree_type = deg_map[degree_type]
    except KeyError:
        raise ValueError("`degree_type` must be either 'in', 'out', 'total', "
                         "or the full version 'in-degree', 'out-degree', "
                         "'total-degree'.")

    return degree_type


# ------------------------- #
# Edge checks and filtering #
# ------------------------- #

def _unique_rows(arr, return_index=False):
    '''
    Keep only unique edges
    '''
    b = np.ascontiguousarray(arr).view(
        np.dtype((np.void, arr.dtype.itemsize * arr.shape[1])))
    b, idx = np.unique(b, return_index=True)
    unique = b.view(arr.dtype).reshape(-1, arr.shape[1]).astype(int)
    if return_index:
        return unique, idx
    return unique


def _no_self_loops(array, return_test=False):
    '''
    Remove self-loops
    '''
    test = array[:, 0] != array[:, 1]
    if return_test:
        return array[test, :].astype(int), test
    return array[test, :].astype(int)


def _filter(ia_edges, ia_edges_tmp, num_ecurrent, edges_hash, b_one_pop,
            multigraph, directed=True, recip_hash=None, distance=None,
            dist_tmp=None):
    '''
    Filter the edges: remove self loops and multiple connections if the graph
    is not a multigraph.
    '''
    if b_one_pop:
        ia_edges_tmp, test = _no_self_loops(ia_edges_tmp, return_test=True)
        if dist_tmp is not None:
            dist_tmp = dist_tmp[test]

    if not multigraph:
        num_ecurrent = len(edges_hash)
        if distance is not None:
            for e, d in zip(ia_edges_tmp, dist_tmp):
                tpl_e = tuple(e)

                if tpl_e not in edges_hash:
                    if directed or tpl_e not in recip_hash:
                        ia_edges[num_ecurrent] = e
                        distance.append(d)
                        edges_hash.add(tpl_e)

                        if not directed:
                            recip_hash.add(tpl_e[::-1])

                        num_ecurrent += 1
        else:
            for e in ia_edges_tmp:
                tpl_e = tuple(e)

                if tpl_e not in edges_hash:
                    if directed or tpl_e not in recip_hash:
                        ia_edges[num_ecurrent] = e

                        edges_hash.add(tpl_e)

                        if not directed:
                            recip_hash.add(tpl_e[::-1])

                        num_ecurrent += 1
    else:
        num_added = len(ia_edges_tmp)
        ia_edges[num_ecurrent:num_ecurrent + num_added, :] = ia_edges_tmp
        num_ecurrent += num_added

        if distance is not None:
            distance.extend(dist_tmp)

    return ia_edges, num_ecurrent


def _cleanup_edges(g, edges, attributes, duplicates, loops, existing, ignore):
    '''
    Cleanup an list of edges.
    '''
    loops_only = loops and not (duplicates or existing)

    new_edges = None
    new_attr  = {}
    directed  = g.is_directed()

    if loops_only:
        edges = np.asarray(edges)

        new_edges, test = _no_self_loops(edges, return_test=True)

        if len(new_edges) != len(edges):
            if ignore:
                _log_message(logger, "WARNING",
                             "Self-loops ignored: {}.".format(edges[~test]))
            else:
                raise InvalidArgument(
                    "Self-loops are present: {}.".format(edges[~test]))

        new_attr  = {k: np.asarray(v)[test] for v, k in attributes.items()}
    else:
        # check (also) either duplicates or existing
        new_attr = {key: [] for key in attributes}
        edge_set = set()

        new_edges = []

        if existing:
            edge_set = {tuple(e) for e in g.edges_array}

        for i, e in enumerate(edges):
            tpl_e = tuple(e)

            if tpl_e in edge_set or (not directed and tpl_e[::-1] in edge_set):
                if ignore:
                    _log_message(logger, "WARNING",
                                 "Existing edge {} ignored.".format(tpl_e))
                else:
                    raise InvalidArgument(
                        "Edge {} already exists.".format(tpl_e))
            elif loops and e[0] == e[1]:
                if ignore:
                    _log_message(logger, "WARNING",
                                 "Self-loop on {} ignored.".format(e[0]))
                else:
                    raise InvalidArgument("Self-loop on {}.".format(e[0]))
            else:
                edge_set.add(tpl_e)
                new_edges.append(tpl_e)

                if not directed:
                    edge_set.add(tpl_e[::-1])

                for k, vv in attributes.items():
                    if nonstring_container(vv):
                        new_attr[k].append(vv[i])
                    else:
                        new_attr[k].append(vv)

        new_edges = np.asarray(new_edges)

    return new_edges, new_attr


# ------------- #
# Distance rule #
# ------------- #

def dist_rule(rule, scale, pos_src, pos_targets, dist=None):
    '''
    DR test from one source to several targets

    Parameters
    ----------
    rule : str
        Either 'exp', 'gaussian', or 'lin'.
    scale : float
        Characteristic scale.
    pos_src : array of shape (2, N)
        Positions of the sources.
    pos_targets : array of shape (2, N)
        Positions of the targets.
    dist : list, optional (default: None)
        List that will be filled with the distances of the edges.

    Returns
    -------
    Array of size N giving the probability of the edges according to the rule.
    '''
    vect = pos_targets - pos_src
    origin = np.array([(0., 0.)])
    # todo correct this
    dist_tmp = np.squeeze(cdist(vect.T, origin), axis=1)
    if dist is not None:
        dist.extend(dist_tmp)
    if rule == 'exp':
        return np.exp(np.divide(dist_tmp, -scale))
    elif rule == 'gaussian':
        return np.exp(-0.5*np.square(np.divide(dist_tmp, scale)))
    elif rule == 'lin':
        return np.divide(scale - dist_tmp, scale).clip(min=0.)
    else:
        raise InvalidArgument('Unknown rule "' + rule + '".')


def max_proba_dist_rule(rule, scale, max_proba, pos_src, pos_targets,
                        dist=None):
    '''
    DR test from one source to several targets

    Parameters
    ----------
    rule : str
        Either 'exp', 'gaussian', or 'lin'.
    scale : float
        Characteristic scale.
    norm : float
        Normalization factor giving proba at zero distance.
    pos_src : 2-tuple
        Positions of the sources.
    pos_targets : array of shape (2, N)
        Positions of the targets.
    dist : list, optional (default: None)
        List that will be filled with the distances of the edges.

    Returns
    -------
    Array of size N giving the probability of the edges according to the rule.
    '''
    x, y = pos_src
    s = np.repeat([[x], [y]], pos_targets.shape[1], axis=1)
    vect = pos_targets - np.repeat([[x], [y]], pos_targets.shape[1], axis=1)
    origin = np.array([(0., 0.)])
    # todo correct this
    dist_tmp = np.squeeze(cdist(vect.T, origin), axis=1)
    if dist is not None:
        dist.extend(dist_tmp)
    if rule == 'exp':
        return max_proba*np.exp(np.divide(dist_tmp, -scale))
    elif rule == 'gaussian':
        return max_proba*np.exp(-0.5*np.square(np.divide(dist_tmp, scale)))
    elif rule == 'lin':
        return max_proba*np.divide(scale - dist_tmp, scale).clip(min=0.)
    else:
        raise InvalidArgument('Unknown rule "' + rule + '".')


def _set_dist_new_edges(new_attr, graph, edge_list):
    ''' Add the distances to the edge attributes '''
    if graph.is_spatial() and "distance" not in new_attr:
        if len(edge_list) == 1:
            positions = graph.get_positions(list(edge_list[0]))
            new_attr["distance"] = cdist([positions[0]], [positions[1]])[0][0]
        else:
            positions = graph.get_positions()
            mat = cdist(positions, positions)
            distances = [mat[e[0], e[1]] for e in edge_list]

            new_attr["distance"] = distances


def _set_default_edge_attributes(g, attributes, num_edges):
    ''' Set default edge attributes values '''
    for k in g.edge_attributes:
        skip = k in ("weight", "distance", "delay")

        if k not in attributes:
            dtype = g.get_attribute_type(k)
            if dtype == "string":
                attributes[k] = ["" for _ in range(num_edges)]
            elif dtype == "double" and not skip:
                attributes[k] = [np.NaN for _ in range(num_edges)]
            elif dtype == "int":
                attributes[k] = [0 for _ in range(num_edges)]
            elif not skip:
                attributes[k] = [None for _ in range(num_edges)]
