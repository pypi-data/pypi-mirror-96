import numpy as np
import logging
from pysnptools.standardizer import Standardizer
from pysnptools.standardizer.unittrained import UnitTrained
import warnings
import pysnptools.util as pstutil

class Unit(Standardizer):
    """A :class:`.Standardizer` to unit standardize SNP data. For each sid, the mean of the values is zero with standard deviation 1.
    NaN values are then filled with zero, the mean (consequently, if there are NaN values, the final standard deviation will not be zero.

    See :class:`.Standardizer` for more information about standardization.

    >>> from pysnptools.standardizer import Unit
    >>> from pysnptools.snpreader import Bed
    >>> from pysnptools.util import example_file # Download and return local file name
    >>> bedfile = example_file("tests/datasets/all_chr.maf0.001.N300.*","*.bed")
    >>> snpdata1 = Bed(bedfile,count_A1=False).read().standardize(Unit())
    >>> print('{0:.6f}'.format(snpdata1.val[0,0]))
    0.229416
    """
    def __init__(self):
        super(Unit, self).__init__()

    def __repr__(self):
        return "{0}()".format(self.__class__.__name__)

    def standardize(self, snps, block_size=None, return_trained=False, force_python_only=False, num_threads=None):
        '''
        When cupy environment variable is set, will use cupy.
        '''
        xp = pstutil.array_module() # Get array module based on any ARRAY_MODULE environ variable.

        if block_size is not None:
            warnings.warn("block_size is deprecated (and not needed, since standardization is in-place", DeprecationWarning)

        if hasattr(snps,"val"):
            snps._val = xp.asarray(snps.val) #If cupy, replace SnpData's val with cupy array
            val = snps.val
        else:
            warnings.warn("standardizing an ndarray instead of a SnpData is deprecated", DeprecationWarning)
            val = snps

        stats = self._standardize_unit_and_beta(val, is_beta=False, a=np.nan, b=np.nan, apply_in_place=True,
                                                use_stats=False,stats=None,num_threads=num_threads, force_python_only=force_python_only)

        if return_trained:
            assert hasattr(snps,"val"), "return_trained=True requires that snps be a SnpData"
            return snps, UnitTrained(snps.sid, stats)
        else:
            return snps

    def _merge_trained(self, trained_list):
        sid = np.concatenate([trained.sid for trained in trained_list])
        stats = np.concatenate([trained.stats for trained in trained_list])
        return UnitTrained(sid, stats)

        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
