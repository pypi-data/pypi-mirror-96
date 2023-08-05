import os
import shutil
import logging
from contextlib import contextmanager
from pysnptools.util.filecache import FileCache

class LocalCache(FileCache):
    '''
    A :class:`.FileCache` for working with files locally.

    See :class:`.FileCache` for general examples of using FileCache.

    This is the simplest :class:`.FileCache` in that it stores everything on a local disk rather than storing things remotely.

    **Constructor:**
        :Parameters: * **directory** (*string*) -- The directory under which files should be written and read.

        :Example:

        >>> from pysnptools.util.filecache import LocalCache
        >>> file_cache = LocalCache('localcache1')
        >>> file_cache.rmtree()
        >>> file_cache.save('sub1/file1.txt','Hello')
        >>> file_cache.file_exists('sub1/file1.txt')
        True

    '''
    def __init__(self,directory):
        super(LocalCache, self).__init__()
        self.directory =  os.path.normpath(directory).replace('\\','/')
        if os.path.exists(self.directory): assert not os.path.isfile(self.directory), "A directory cannot exist where a file already exists."

    def __repr__(self): 
        return "{0}('{1}')".format(self.__class__.__name__,self.directory)

    @property
    def name(self):
        '''
        A path-like name for this `LocalCache`.

        :rtype: string
        '''
        return self.directory

    def _simple_file_exists(self,simple_file_name):
        full_file = self.directory + "/" + simple_file_name
        return os.path.exists(full_file) and os.path.isfile(full_file)

    @contextmanager
    def _simple_open_read(self,simple_file_name,updater=None):
        logging.info("open_read('{0}')".format(simple_file_name))
        file_name = self.directory + "/" + simple_file_name
        assert os.path.exists(file_name), "File doesn't exist in LocalCache. File is '{0}'".format(file_name)

        yield file_name

        logging.info("close('{0}')".format(simple_file_name))

    @contextmanager
    def _simple_open_write(self,simple_file_name,size=0,updater=None):
        import pysnptools.util as pstutil # put here to avoid recursive nesting

        logging.info("open_write('{0}',size={1})".format(simple_file_name,size))

        #Register the file name in the directory
        file_name=self.directory + "/" + simple_file_name
        if os.path.exists(file_name): #This is only OK, if it is a directory containing no files (and thus doesn't exist)
            assert not os.path.isfile(file_name), "Can't open a file for write if it already exists."
            assert not self._at_least_one(self.walk(simple_file_name)), "Can't open a file for write if a directory with files already has the same name ({0},{1})".format(self,simple_file_name)
            shutil.rmtree(file_name)
        else:
            pstutil.create_directory_if_necessary(file_name,isfile=True)

        yield file_name

        logging.info("close('{0}')".format(simple_file_name))
        assert os.path.exists(file_name), "File doesn't exist in LocalCache. File is '{0}'".format(file_name)

    def _simple_rmtree(self,updater=None):
        logging.info("rmtree -- {0}".format(self.directory))
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)

    def _simple_remove(self,simple_file_name, updater=None):
        full_file = self.directory + "/" + simple_file_name
        assert os.path.exists(full_file) and os.path.isfile(full_file), "Expect file to exist (and be a file)"
        os.remove(full_file) #We don't actually remove the folders from the disk, but to this API the folder is gone.

    def _simple_getmtime(self,simple_file_name):
        full_file = self.directory + "/" + simple_file_name
        assert os.path.exists(full_file) and os.path.isfile(full_file), "Expect file to exist (and be a file)"
        return os.path.getmtime(full_file)

    def _simple_join(self,path):
        directory = self.directory + "/" + path
        if os.path.exists(directory): assert not os.path.isfile(directory), "Can't treat an existing file as a directory"
        return LocalCache(directory)

            
            

    def _simple_walk(self):
        for root, dirs, files in os.walk(self.directory):
            root = os.path.normpath(root).replace('\\','/')
            rel = os.path.relpath(root,self.directory).replace('\\','/')
            for file in files:
                yield file if rel == "." else rel + "/" + file



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
