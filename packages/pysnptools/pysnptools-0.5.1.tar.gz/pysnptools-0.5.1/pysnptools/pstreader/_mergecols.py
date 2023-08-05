import logging
import os
import numpy as np
from pysnptools.pstreader import PstReader


#!!! would be better to make a Transpose class that could term _mergerows into mergecols? Be sure special Bed code is still there.
class _MergeCols(PstReader):
    def __init__(self,reader_list,cache_file=None,skip_check=False):
        super(_MergeCols, self).__init__()
        assert len(reader_list) > 0, "Expect at least one reader"
        self.skip_check = skip_check

        self.reader_list = reader_list
        self._repr_string = "_MergeCols({0})".format(",".join([str(s) for s in reader_list]))

        if cache_file is not None:
            #!!!add warning if cache_file doesn't end with .npz
            if not os.path.exists(cache_file):
                self._run_once()
                self._savez(cache_file)
            else:
                self._load(cache_file)

        def _savez(self, cache_file):
            np.savez(cache_file,
                     _row=self._row, _row_property=self._row_property,
                     _col=self._col, _col_property=self._col_property,
                     col_count_list=self.col_count_list)

        def _load(self,cache_file):
                with np.load(cache_file,allow_pickle=True) as data:
                    self._col = data['_col']
                    self._col_property = data['_col_property']
                    self.col_count_list = data['col_count_list']
                    assert ('_row' in data) == ('_row_property' in data)
                    self._row = data['_row']
                    self._row_property = data['_row_property']

    def _run_once(self):
        if hasattr(self,'_has_run_once'):
            return
        from pysnptools.snpreader import Bed
        self._has_run_once = True
        #Check that all rows are distinct and that all cols and pos are the same and in the same order

        if self.skip_check and all(isinstance(reader,Bed) for reader in self.reader_list): #Special code if all Bed readers
            l = [SnpReader._read_map_or_bim(reader.filename,remove_suffix="bed", add_suffix="bim") for reader in self.reader_list]
            self.col_count_list = np.array([len(ll[0]) for ll in l])
            self._row = self.reader_list[0].row
            self._row_property = self.reader_list[0].row_property
            self._col = np.concatenate([ll[0] for ll in l])
            self._col_property = np.concatenate([ll[1] for ll in l])
        else:
            col_list = []
            col_property_list = []
            col_set = set()
            self.col_count_list = []
            self._row = self.reader_list[0].row
            self._row_property = self.reader_list[0].row_property
            for reader_index,reader in enumerate(self.reader_list):
                if reader_index % 10 == 0: logging.info("_MergeCols looking at reader #{0}: {1}".format(reader_index,reader))
                if not self.skip_check:
                    assert np.array_equal(self._row,reader.row), "Expect rows to be the same across all files"
                    np.testing.assert_equal(self._row_property,reader.row_property) #"Expect column_property to be the same across all files"
                    size_before = len(col_set)
                    col_set.update((tuple(item) for item in reader.col))
                    assert len(col_set) == size_before + reader.col_count, "Expect cols to be distinct in all files"
                col_list.append(reader.col)
                col_property_list.append(reader.col_property)
                self.col_count_list.append(reader.col_count)
            self._col = np.concatenate(col_list)
            self._col_property = np.concatenate(col_property_list)
            self.col_count_list = np.array(self.col_count_list)

    @property
    def col(self):
        self._run_once()
        return self._col

    @property
    def row(self):
        self._run_once()
        return self._row

    @property
    def col_property(self):
        self._run_once()
        return self._col_property

    @property
    def row_property(self):
        self._run_once()
        return self._row_property

    def __repr__(self): 
        #Don't need _run_once because based only on initial info
        return self._repr_string

    def copyinputs(self, copier):
        self._run_once()
        for reader in self.reader_list:
            copier.input(reader)

    def _create_reader_and_col_index_list(self,col_index):
        result = []
        start = 0
        for reader_index in range(len(self.reader_list)):
            stop = start + self.col_count_list[reader_index] #!!! shouldn't this be col_count (and check _mergerows, too)
            is_here = (col_index >= start) * (col_index < stop)
            if any(is_here):
                col_index_rel = col_index[is_here]-start
                result.append((reader_index,is_here,col_index_rel))
            start = stop
        return result

    def _read(self, row_index_or_none, col_index_or_none, order, dtype, force_python_only, view_ok, num_threads):
        #!!!tests to do: no row's
        #!!!tests to do: no col's
        #!!!test to do: from file 1, file2, and then file1 again
        dtype = np.dtype(dtype)
        col_index = col_index_or_none if col_index_or_none is not None else np.arange(self.col_count) #!!!might want to special case reading all
        row_index_or_none_count = self.row_count if row_index_or_none is None else len(row_index_or_none)
        col_index_or_none_count = self.col_count if col_index_or_none is None else len(col_index_or_none)

        #Create a list of (reader,col_index)
        reader_and_col_index_list = self._create_reader_and_col_index_list(col_index)
        if len(reader_and_col_index_list) == 0:
            return self.reader_list[0]._read(row_index_or_none,col_index,order,dtype,force_python_only, view_ok, num_threads)
        elif len(reader_and_col_index_list) == 1:
            reader_index,col_index_in,col_index_rel = reader_and_col_index_list[0]
            reader = self.reader_list[reader_index]
            return reader._read(row_index_or_none,col_index_rel,order,dtype,force_python_only, view_ok, num_threads)
        else:
            logging.info("Starting read from {0} subreaders".format(len(reader_and_col_index_list)))
            if order == 'A' or order is None:#LATER does every _read( need code like this?
                order = 'F'
            val = None

            for reader_index,is_here,col_index_rel in reader_and_col_index_list:
                reader = self.reader_list[reader_index]
                if reader_index % 1 == 0: logging.info("Reading from #{0}: {1}".format(reader_index,reader))
                piece = reader._read(row_index_or_none,col_index_rel,order,dtype,force_python_only, view_ok=True, num_threads=num_threads)
                if val is None:
                    if len(piece.shape) == 2:
                        val = np.empty([row_index_or_none_count, col_index_or_none_count], dtype=dtype, order=order)
                    else:
                        val = np.empty([row_index_or_none_count, col_index_or_none_count, self.val_shape], dtype=dtype, order=order)
                    val.fill(np.nan) #LATER Keep this?

                if len(val.shape)== 2:
                    val[:,is_here] = piece 
                else:
                    val[:,is_here,:] = piece

            logging.info("Ended read from {0} subreaders".format(len(reader_and_col_index_list)))
            assert val is not None
            return val

