#
# Copyright (C) 2017-2020  Leo Singer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Support for HEALPix UNIQ pixel indexing [1]_ and multi-order coverage (MOC)
maps [2]_.

References
----------
.. [1] Reinecke & Hivon, 2015. "Efficient data structures for masks on 2D
       grids." AA 580, A132. :doi:`10.1051/0004-6361/201526549`
.. [2] Boch et al., 2014. "MOC - HEALPix Multi-Order Coverage map." IVOA
       Recommendation <http://ivoa.net/documents/MOC/>.

"""

from astropy import table
import numpy as np
from numpy.lib.recfunctions import repack_fields

from .core import nest2uniq, uniq2nest, uniq2order, uniq2pixarea, uniq2ang
from .core import rasterize as _rasterize
from .util.numpy import add_newdoc_ufunc, require_contiguous_aligned

__all__ = ('nest2uniq', 'uniq2nest', 'uniq2order', 'uniq2pixarea',
           'uniq2ang', 'rasterize')


add_newdoc_ufunc(nest2uniq, """\
Convert a pixel index from NESTED to NUNIQ ordering.

Parameters
----------
order : `numpy.ndarray`
    HEALPix resolution order, the logarithm base 2 of `nside`
ipix : `numpy.ndarray`
    NESTED pixel index

Returns
-------
uniq : `numpy.ndarray`
    NUNIQ pixel index

""")
nest2uniq = require_contiguous_aligned(nest2uniq)


add_newdoc_ufunc(uniq2order, """\
Determine the HEALPix resolution order of a HEALPix NESTED index.

Parameters
----------
uniq : `numpy.ndarray`
    NUNIQ pixel index

Returns
-------
order : `numpy.ndarray`
    HEALPix resolution order, the logarithm base 2 of `nside`

""")
uniq2order = require_contiguous_aligned(uniq2order)


add_newdoc_ufunc(uniq2pixarea, """\
Determine the area of a HEALPix NESTED index.

Parameters
----------
uniq : `numpy.ndarray`
    NUNIQ pixel index

Returns
-------
area : `numpy.ndarray`
    The pixel's area in steradians

""")
uniq2pixarea = require_contiguous_aligned(uniq2pixarea)


add_newdoc_ufunc(uniq2nest, """\
Convert a pixel index from NUNIQ to NESTED ordering.

Parameters
----------
uniq : `numpy.ndarray`
    NUNIQ pixel index

Returns
-------
order : `numpy.ndarray`
    HEALPix resolution order (logarithm base 2 of `nside`)
ipix : `numpy.ndarray`
    NESTED pixel index

""")
uniq2nest = require_contiguous_aligned(uniq2nest)


def rasterize(moc_data, order=None):
    """Convert a multi-order HEALPix dataset to fixed-order NESTED ordering.

    Parameters
    ----------
    moc_data : `numpy.ndarray`
        A multi-order HEALPix dataset stored as a Numpy record array whose
        first column is called UNIQ and contains the NUNIQ pixel index. Every
        point on the unit sphere must be contained in exactly one pixel in the
        dataset.
    order : int, optional
        The desired output resolution order, or :obj:`None` for the maximum
        resolution present in the dataset.

    Returns
    -------
    nested_data : `numpy.ndarray`
        A fixed-order, NESTED-ordering HEALPix dataset with all of the columns
        that were in moc_data, with the exception of the UNIQ column.

    """
    if order is None or order < 0:
        order = -1
    else:
        orig_order, orig_nest = uniq2nest(moc_data['UNIQ'])
        to_downsample = order < orig_order
        if np.any(to_downsample):
            to_keep = table.Table(moc_data[~to_downsample], copy=False)
            orig_order = orig_order[to_downsample]
            orig_nest = orig_nest[to_downsample]
            to_downsample = table.Table(moc_data[to_downsample], copy=False)

            ratio = 1 << (2 * np.int64(orig_order - order))
            weights = 1.0 / ratio
            for colname, column in to_downsample.columns.items():
                if colname != 'UNIQ':
                    column *= weights
            to_downsample['UNIQ'] = nest2uniq(order, orig_nest // ratio)
            to_downsample = to_downsample.group_by(
                'UNIQ').groups.aggregate(np.sum)

            moc_data = table.vstack((to_keep, to_downsample))

    # Ensure that moc_data has appropriate padding for each of its columns to
    # be properly aligned in order to avoid undefined behavior.
    moc_data = repack_fields(np.asarray(moc_data), align=True)

    return _rasterize(moc_data, order=order)


del add_newdoc_ufunc, require_contiguous_aligned
