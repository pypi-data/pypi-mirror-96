
# This file is part of PyEMMA.
#
# Copyright (c) 2015, 2014 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

r"""This module implements IO and manipulation function for discrete trajectories

Discrete trajectories are generally ndarrays of type integer
We store them either as single column ascii files or as ndarrays of shape (n,) in binary .npy format.

.. moduleauthor:: B. Trendelkamp-Schroer <benjamin DOT trendelkamp-schroer AT fu-berlin DOT de>
.. moduleauthor:: F. Noe <frank DOT noe AT fu-berlin DOT de>

"""
from functools import reduce
import warnings
import numpy as np
from pyemma.util.types import ensure_dtraj_list as _ensure_dtraj_list
from pyemma.util.annotators import shortcut


__author__ = 'noe'

################################################################################
# ascii
################################################################################

@shortcut('read_dtraj')
def read_discrete_trajectory(filename):
    """Read discrete trajectory from ascii file.

    The ascii file containing a single column with integer entries is
    read into an array of integers.

    Parameters
    ----------
    filename : str
        The filename of the discrete state trajectory file.
        The filename can either contain the full or the
        relative path to the file.

    Returns
    -------
    dtraj : (M, ) ndarray
        Discrete state trajectory.

    """
    with open(filename, "r") as f:
        lines=f.read()
        dtraj=np.fromstring(lines, dtype=int, sep="\n")
        return dtraj


@shortcut('write_dtraj')
def write_discrete_trajectory(filename, dtraj):
    r"""Write discrete trajectory to ascii file.

    The discrete trajectory is written to a
    single column ascii file with integer entries

    Parameters
    ----------
    filename : str
        The filename of the discrete state trajectory file.
        The filename can either contain the full or the
        relative path to the file.

    dtraj : array-like
        Discrete state trajectory.

    """
    dtraj=np.asarray(dtraj)
    with open(filename, 'w') as f:
        dtraj.tofile(f, sep='\n', format='%d')

################################################################################
# binary
################################################################################

@shortcut('load_dtraj')
def load_discrete_trajectory(filename):
    r"""Read discrete trajectory form binary file.

    The binary file is a one dimensional numpy array
    of integers stored in numpy .npy format.

    Parameters
    ----------
    filename : str
        The filename of the discrete state trajectory file.
        The filename can either contain the full or the
        relative path to the file.

    Returns
    -------
    dtraj : (M,) ndarray
        Discrete state trajectory.

    """
    dtraj=np.load(filename)
    return dtraj


@shortcut('save_dtraj')
def save_discrete_trajectory(filename, dtraj):
    r"""Write discrete trajectory to binary file.

    The discrete trajectory is stored as ndarray of integers
    in numpy .npy format.

    Parameters
    ----------
    filename : str
        The filename of the discrete state trajectory file.
        The filename can either contain the full or the
        relative path to the file.


    dtraj : array-like
        Discrete state trajectory.

    """
    dtraj=np.asarray(dtraj)
    np.save(filename, dtraj)


################################################################################
# simple statistics
################################################################################


@shortcut('histogram')
def count_states(dtrajs, ignore_negative=False):
    r"""returns a histogram count

    Parameters
    ----------
    dtrajs : array_like or list of array_like
        Discretized trajectory or list of discretized trajectories
    ignore_negative, bool, default=False
        Ignore negative elements. By default, a negative element will cause an
        exception

    Returns
    -------
    count : ndarray((n), dtype=int)
        the number of occurrences of each state. n=max+1 where max is the largest state index found.

    """
    # format input
    dtrajs = _ensure_dtraj_list(dtrajs)
    # make bincounts for each input trajectory
    nmax = 0
    bcs = []
    for dtraj in dtrajs:
        if ignore_negative:
            dtraj = dtraj[np.where(dtraj >= 0)]
        bc = np.bincount(dtraj)
        nmax = max(nmax, bc.shape[0])
        bcs.append(bc)
    # construct total bincount
    res = np.zeros(nmax, dtype=int)
    # add up individual bincounts
    for i, bc in enumerate(bcs):
        res[:bc.shape[0]] += bc
    return res


def visited_set(dtrajs):
    r"""returns the set of states that have at least one count

    Parameters
    ----------
    dtraj : array_like or list of array_like
        Discretized trajectory or list of discretized trajectories

    Returns
    -------
    vis : ndarray((n), dtype=int)
        the set of states that have at least one count.
    """
    hist = count_states(dtrajs)
    return np.argwhere(hist > 0)[:,0]


@shortcut('nstates')
def number_of_states(dtrajs, only_used = False):
    r"""returns the number of states in the given trajectories.

    Parameters
    ----------
    dtrajs : array_like or list of array_like
        Discretized trajectory or list of discretized trajectories
    only_used = False : boolean
        If False, will return max+1, where max is the largest index used.
        If True, will return the number of states that occur at least once.
    """
    dtrajs = _ensure_dtraj_list(dtrajs)
    if only_used:
        # only states with counts > 0 wanted. Make a bincount and count nonzeros
        bc = count_states(dtrajs)
        return np.count_nonzero(bc)
    else:
        # all states wanted, included nonpopulated ones. return max + 1
        imax = 0
        for dtraj in dtrajs:
            imax = max(imax, np.max(dtraj))
        return imax+1

################################################################################
# indexing
################################################################################

def rewrite_dtrajs_to_core_sets(dtrajs, core_set, in_place=False):
    r""" Rewrite trajectories that contain unassigned states.

    The given discrete trajectories are rewritten such that states not in the core
    set are -1. Trajectories that begin with unassigned states will be truncated here.
    Index offsets are computed to keep assignment to original data.

    Examples
    --------
    Let's assume we want to restrict the core sets to 1, 2 and 3:

    >>> import numpy as np
    >>> dtrajs = [np.array([5, 4, 1, 3, 4, 4, 5, 3, 0, 1]),
    ...           np.array([4, 4, 4, 5]),
    ...           np.array([4, 4, 5, 1, 2, 3])]
    >>> dtraj_core, offsets, n_cores = rewrite_dtrajs_to_core_sets(dtrajs, core_set=[0, 1, 3])
    >>> print(dtraj_core)
    [array([ 1,  3, -1, -1, -1,  3,  0,  1]), array([ 1, -1,  3])]

    We reach the first milestone in the first trajectory after two steps, after four in the second and so on:
    >>> print(offsets)
    [2, None, 3]

    Since the second trajectory never visited a core set, it will be removed and marked as such in the offsets
    lists by a 'None'. Each entry corresponds to one entry in the input list.

    Parameters
    ----------
    dtrajs: array_like or list of array_like
        Discretized trajectory or list of discretized trajectories.

    core_set: array -like of ints
        Pass an array of micro-states to define the core sets.

    in_place: boolean, default=False
        if True, replace the current dtrajs
        if False, return a copy

    Returns
    -------
    dtrajs, offsets, n_cores: list of ndarray(dtype=int), list, int

    """
    import copy
    from pyemma.util import types

    dtrajs = types.ensure_dtraj_list(dtrajs)

    if isinstance(core_set, (list, tuple)):
        core_set = list(map(types.ensure_int_vector, core_set))
        core_set = np.unique(np.concatenate(core_set))
    else:
        core_set = np.unique(types.ensure_int_vector(core_set))

    n_cores = len(core_set)

    if not in_place:
        dtrajs = copy.deepcopy(dtrajs)

    # if we have no state definition at the beginning of a trajectory, we store the offset to the first milestone.
    offsets = [0]*len(dtrajs)

    for i, d in enumerate(dtrajs):
        # set non-core states to -1
        outside_core_set = ~np.in1d(d, core_set)
        if not np.any(outside_core_set):
            continue
        d[outside_core_set] = -1

        where_positive = np.where(d >= 0)[0]
        offsets[i] = where_positive.min() if len(where_positive) > 0 else None
        # traj never reached a core set?
        if offsets[i] is None:
            warnings.warn('The entire trajectory with index {i} never visited a core set!'.format(i=i))
        elif offsets[i] > 0:
            warnings.warn('The trajectory with index {i} had to be truncated for not starting in a core.'.format(i=i))
            dtrajs[i] = d[np.where(d >= 0)[0][0]:]


    # filter empty dtrajs
    dtrajs = [d for i,d in enumerate(dtrajs)
              if offsets[i] is not None
              ]

    return dtrajs, offsets, n_cores


def _apply_offsets_to_samples(indices, offsets):
    r""" This private function applies the given offsets returned by the milestone_counting function to
    the results of the sample_indexes_by_* functions.

    This is necessary in order to obtain the right order in the input files.

    Notes
    -----
    Operates in place.

    Parameters
    ----------
    indices :  list of ndarray( (N, 2) )
        trajectory and corresponding frame indices of original input
    offsets: dict {itraj, offset}

    """
    from pyemma.util import types
    assert types.is_int_matrix(indices)
    assert isinstance(offsets, list), offsets

    # 1. restore itraj indices (the mapping is relative to the original oder)
    last_valid = None
    n_missing = 0
    for itraj, offset in enumerate(offsets):
        if offset is None:  # this itraj is missing
            n_missing += 1
        else:
            if n_missing > 0:
                # shift subsequent indices by n_missing
                indices[indices[:, 0] > last_valid, 0] += n_missing
            last_valid = itraj
            n_missing = 0

    # 2. restore frame indices (relative to org order)
    for itraj, offset in enumerate(offsets):
        if offset is None:
            continue
        indices[indices[:, 0] == itraj, 1] += offset


def index_states(dtrajs, subset=None):
    """Generates a trajectory/time indexes for the given list of states

    Parameters
    ----------
    dtraj : array_like or list of array_like
        Discretized trajectory or list of discretized trajectories. Negative elements will be ignored
    subset : ndarray((n)), optional, default = None
        array of states to be indexed. By default all states in dtrajs will be used

    Returns
    -------
    indexes : list of ndarray( (N_i, 2) )
        For each state, all trajectory and time indexes where this state occurs.
        Each matrix has a number of rows equal to the number of occurrences of the corresponding state,
        with rows consisting of a tuple (i, t), where i is the index of the trajectory and t is the time index
        within the trajectory.

    """
    # check input
    dtrajs = _ensure_dtraj_list(dtrajs)
    # select subset unless given
    n = number_of_states(dtrajs)
    if subset is None:
        subset = np.arange(n)
    else:
        if np.max(subset) >= n:
            raise ValueError('Selected subset is not a subset of the states in dtrajs.')
    # histogram states
    hist = count_states(dtrajs, ignore_negative=True)
    # efficient access to which state are accessible
    is_requested = np.ndarray((n), dtype=bool)
    is_requested[:] = False
    is_requested[subset] = True
    # efficient access to requested state indexes
    full2states = np.zeros((n), dtype=int)
    full2states[subset] = range(len(subset))
    # initialize results
    res    = np.ndarray(len(subset), dtype=object)
    counts = np.zeros((len(subset)), dtype=int)
    for i,s in enumerate(subset):
        res[i] = np.zeros((hist[s],2), dtype=int)
    # walk through trajectories and remember requested state indexes
    for i,dtraj in enumerate(dtrajs):
        for t,s in enumerate(dtraj):
            # only index nonnegative state indexes
            if s >= 0 and is_requested[s]:
                k = full2states[s]
                res[k][counts[k],0] = i
                res[k][counts[k],1] = t
                counts[k] += 1
    return res

################################################################################
# sampling from state indexes
################################################################################


def sample_indexes_by_sequence(indexes, sequence):
    """Samples trajectory/time indexes according to the given sequence of states

    Parameters
    ----------
    indexes : list of ndarray( (N_i, 2) )
        For each state, all trajectory and time indexes where this state occurs.
        Each matrix has a number of rows equal to the number of occurrences of the corresponding state,
        with rows consisting of a tuple (i, t), where i is the index of the trajectory and t is the time index
        within the trajectory.
    sequence : array of integers
        A sequence of discrete states. For each state, a trajectory/time index will be sampled at which dtrajs
        have an occurrences of this state

    Returns
    -------
    indexes : ndarray( (N, 2) )
        The sampled index sequence.
        Index array with a number of rows equal to N=len(sequence), with rows consisting of a tuple (i, t),
        where i is the index of the trajectory and t is the time index within the trajectory.

    """
    N = len(sequence)
    res = np.zeros((N,2), dtype=int)
    for t in range(N):
        s = sequence[t]
        i = np.random.randint(indexes[s].shape[0])
        res[t,:] = indexes[s][i,:]

    return res


def sample_indexes_by_state(indexes, nsample, subset=None, replace=True):
    """Samples trajectory/time indexes according to the given sequence of states

    Parameters
    ----------
    indexes : list of ndarray( (N_i, 2) )
        For each state, all trajectory and time indexes where this state occurs.
        Each matrix has a number of rows equal to the number of occurrences of the corresponding state,
        with rows consisting of a tuple (i, t), where i is the index of the trajectory and t is the time index
        within the trajectory.
    nsample : int
        Number of samples per state. If replace = False, the number of returned samples per state could be smaller
        if less than nsample indexes are available for a state.
    subset : ndarray((n)), optional, default = None
        array of states to be indexed. By default all states in dtrajs will be used
    replace : boolean, optional
        Whether the sample is with or without replacement

    Returns
    -------
    indexes : list of ndarray( (N, 2) )
        List of the sampled indices by state.
        Each element is an index array with a number of rows equal to N=len(sequence), with rows consisting of a
        tuple (i, t), where i is the index of the trajectory and t is the time index within the trajectory.

    """
    # how many states in total?
    n = len(indexes)
    # define set of states to work on
    if subset is None:
        subset = np.arange(n)

    # list of states
    res = np.ndarray(len(subset), dtype=object)
    for i, s in enumerate(subset):
        # how many indexes are available?
        m_available = indexes[s].shape[0]
        # do we have no indexes for this state? Then insert empty array.
        if m_available == 0:
            res[i] = np.zeros((0, 2), dtype=int)
        elif replace:
            I = np.random.choice(m_available, nsample, replace=True)
            res[i] = indexes[s][I,:]
        else:
            I = np.random.choice(m_available, min(m_available,nsample), replace=False)
            res[i] = indexes[s][I,:]

    return res


def sample_indexes_by_distribution(indexes, distributions, nsample):
    """Samples trajectory/time indexes according to the given probability distributions

    Parameters
    ----------
    indexes : list of ndarray( (N_i, 2) )
        For each state, all trajectory and time indexes where this state occurs.
        Each matrix has a number of rows equal to the number of occurrences of the corresponding state,
        with rows consisting of a tuple (i, t), where i is the index of the trajectory and t is the time index
        within the trajectory.
    distributions : list or array of ndarray ( (n) )
        m distributions over states. Each distribution must be of length n and must sum up to 1.0
    nsample : int
        Number of samples per distribution. If replace = False, the number of returned samples per state could be smaller
        if less than nsample indexes are available for a state.

    Returns
    -------
    indexes : length m list of ndarray( (nsample, 2) )
        List of the sampled indices by distribution.
        Each element is an index array with a number of rows equal to nsample, with rows consisting of a
        tuple (i, t), where i is the index of the trajectory and t is the time index within the trajectory.

    """
    # how many states in total?
    n = len(indexes)
    for dist in distributions:
        if len(dist) != n:
            raise ValueError('Size error: Distributions must all be of length n (number of states).')

    # list of states
    res = np.ndarray(len(distributions), dtype=object)
    for i, dist in enumerate(distributions):
        # sample states by distribution
        sequence = np.random.choice(n, size=nsample, p=dist)
        res[i] = sample_indexes_by_sequence(indexes, sequence)
    #
    return res
