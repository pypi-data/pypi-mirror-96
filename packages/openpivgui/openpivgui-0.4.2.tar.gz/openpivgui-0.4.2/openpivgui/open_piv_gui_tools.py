#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Methods for reuse within the OpenPivGui project.'''

import numpy as np
import math
import os
__licence__ = '''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__email__ = 'vennemann@fh-muenster.de'


def str2list(s):
    '''Parses a string representation of a list.

    Parameters
    ----------
    s : str
        String containing comma separated values.

    Example
    -------
    str2list('img01.png', 'img02.png')

    Returns
    -------
    list
    '''
    return([t.strip("' ") for t in s.strip('(),').split(',')])


def str2dict(s):
    '''Parses a string representation of a dictionary.

    Parameters
    ----------
    s : str
        Comma separated list of colon separated key value pairs.

    Example
    -------
    str2dict('key1: value1', 'key2: value2')
    '''
    d = {}
    l = str2list(s)
    for elem in l:
        key, value = elem.split(':')
        key.strip(' ')
        value.strip(' ')
        d.update({key: value})
    return(d)


def create_save_vec_fname(path=os.getcwd(),
                          basename=None,
                          postfix='',
                          count=-1,
                          max_count=9):
    '''Assembles a valid absolute path for saving vector data.

    Parameters
    ----------
    path : str
        Directory path. Default: Working directory.
    basename : str
        Prefix. Default: None.
    postfix : str
        Postfix. Default: None.
    count : int
        Counter for numbering filenames. 
        Default: -1 (no number)
    max_count : int
        Highest number to expect. Used for generating 
        leading zeros. Default: 9 (no leading zeros).
    '''
    if count == -1:
        num = ''
    else:
        num = str(count).zfill(math.ceil(math.log10(max_count)))
    if basename is None:
        basename = os.path.basename(path)
    elif basename == '':
        basename = 'out'
    return(os.path.dirname(path) +
           os.sep +
           basename.split('.')[0] +
           postfix +
           num +
           '.vec')


def get_dim(array):
    '''Computes dimension of vector data.

    Assumes data to be organised as follows (example):
    x  y  v_x v_y
    16 16 4.5 3.2
    32 16 4.3 3.1
    16 32 4.2 3.5
    32 32 4.5 3.2

    Parameters
    ----------
    array : np.array
        Flat numpy array.

    Returns
    -------
    tuple
        Dimension of the vector field (x, y).
    '''
    return(len(set(array[:, 0])),
           len(set(array[:, 1])))


def save(x, y, u, v, mask, sig2noise, filename, fmt='%8.4f', delimiter='\t'):
    out = np.vstack([m.ravel() for m in [x, y, u, v, mask, sig2noise]])
    np.savetxt(filename, out.T, fmt=fmt, delimiter=delimiter)

    

def _round(number, decimals = 0):
    multiplier = 10 **decimals
    return(math.floor(number * multiplier + 0.5) / multiplier) 