"""S3 Parquet Data Feeder."""


from __future__ import annotations

import datetime
from functools import lru_cache, partial
from itertools import chain
from logging import Logger
import math
from pathlib import Path
import os
import random
import re
import time
from typing import Any, Optional, Union
from typing import Collection, Dict, List, Set, Tuple   # Py3.9+: use built-ins
from urllib.parse import ParseResult, urlparse
from uuid import uuid4
# from warnings import simplefilter

from numpy import isfinite, ndarray, vstack
from pandas import DataFrame, Series, concat, isnull, notnull, read_parquet
# from pandas.errors import PerformanceWarning
from pandas._libs.missing import NAType   # pylint: disable=no-name-in-module
from tqdm import tqdm

from pyarrow.dataset import dataset
from pyarrow.fs import LocalFileSystem, S3FileSystem
from pyarrow.lib import RecordBatch, Schema, Table   # pylint: disable=no-name-in-module
from pyarrow.parquet import FileMetaData, read_metadata, read_schema, read_table

from h1st.utils import debug, fs, s3
from h1st.utils.data_types.arrow import (
    DataType, _ARROW_STR_TYPE, _ARROW_DATE_TYPE,
    is_binary, is_boolean, is_num, is_possible_cat, is_possible_feature, is_string)
from h1st.utils.data_types.numpy_pandas import NUMPY_FLOAT_TYPES, NUMPY_INT_TYPES
from h1st.utils.data_types.python import (PY_NUM_TYPES, PyNumType,
                                          PyPossibleFeatureType, PY_LIST_OR_TUPLE)
from h1st.utils.default_dict import DefaultDict
from h1st.utils.iter import to_iterable
from h1st.utils.namespace import Namespace, DICT_OR_NAMESPACE_TYPES

from ._abstract import (AbstractDataHandler, AbstractFileDataHandler, AbstractS3FileDataHandler,
                        ColsType, ReducedDataSetType)
from .pandas import PandasMLPreprocessor


__all__ = ('ParquetDataset',)


# flake8: noqa
# (too many camelCase names)

# pylint: disable=c-extension-no-member
# e.g., `math.`

# pylint: disable=invalid-name
# e.g., camelCase names

# pylint: disable=no-member
# e.g., `._cache`

# pylint: disable=protected-access
# e.g., `._cache`

# pylint: disable=too-many-lines
# (this whole module)


# TODO: revisit Pandas PeformanceWarning
# github.com/twopirllc/pandas-ta/issues/340#issuecomment-879450854
# simplefilter(action='ignore', category=PerformanceWarning)


def randomSample(population: Collection[Any], sampleSize: int,
                 returnCollectionType=set) -> Collection[Any]:
    """Draw random sample from population."""
    return returnCollectionType(random.sample(population=population, k=sampleSize)
                                if len(population) > sampleSize
                                else population)


class ParquetDataset(AbstractS3FileDataHandler):
    # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """S3 Parquet Data Feeder."""

    # caches
    _CACHE: Dict[str, Namespace] = {}
    _FILE_CACHES: Dict[str, Namespace] = {}

    # default arguments dict
    # (cannot be h1st.utils.namespace.Namespace
    # because that makes nested dicts into normal dicts)
    _DEFAULT_KWARGS: Dict[str, Optional[Union[str, DefaultDict]]] = dict(
        iCol=None, tCol=None,

        reprSampleMinNFiles=AbstractFileDataHandler._REPR_SAMPLE_MIN_N_FILES,
        reprSampleSize=AbstractDataHandler._DEFAULT_REPR_SAMPLE_SIZE,

        nulls=DefaultDict((None, None)),
        minNonNullProportion=DefaultDict(AbstractDataHandler._DEFAULT_MIN_NON_NULL_PROPORTION),
        outlierTailProportion=DefaultDict(AbstractDataHandler._DEFAULT_OUTLIER_TAIL_PROPORTION),
        maxNCats=DefaultDict(AbstractDataHandler._DEFAULT_MAX_N_CATS),
        minProportionByMaxNCats=DefaultDict(
            AbstractDataHandler._DEFAULT_MIN_PROPORTION_BY_MAX_N_CATS))

    def __init__(self, path: str, *, awsRegion: Optional[str] = None,
                 accessKey: Optional[str] = None, secretKey: Optional[str] = None,   # noqa: E501
                 _mappers: Optional[callable] = None,
                 _reduceMustInclCols: Optional[ColsType] = None,
                 verbose: bool = True, **kwargs: Any):
        # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        """Init S3 Parquet Data Feeder."""
        if verbose or debug.ON:
            logger: Logger = self.classStdOutLogger()

        self.awsRegion: Optional[str] = awsRegion
        self.accessKey: Optional[str] = accessKey
        self.secretKey: Optional[str] = secretKey

        self.onS3: bool = path.startswith('s3://')
        if self.onS3:
            self.s3Client = s3.client(region=awsRegion, access_key=accessKey, secret_key=secretKey)

        self.path: str = path if self.onS3 else os.path.expanduser(path)

        if self.path in self._CACHE:
            _cache: Namespace = self._CACHE[self.path]
        else:
            self._CACHE[self.path] = _cache = Namespace()

        if _cache:
            if debug.ON:
                logger.debug(msg=f'*** RETRIEVING CACHE FOR "{self.path}" ***')

        else:
            if self.onS3:
                _parsedURL: ParseResult = urlparse(url=path, scheme='', allow_fragments=True)
                _cache.s3Bucket = _parsedURL.netloc
                _cache.pathS3Key = _parsedURL.path[1:]

            if self.path in self._FILE_CACHES:
                _cache.nFiles = 1
                _cache.filePaths = {self.path}

            else:
                if verbose:
                    logger.info(msg=(msg := f'Loading "{self.path}" by Arrow...'))
                    tic: float = time.time()

                if self.onS3:
                    s3.rm(path=path,
                          is_dir=True,
                          globs='*_$folder$',   # redundant AWS EMR-generated files
                          quiet=True,
                          verbose=False)

                _cache._srcArrowDS = dataset(source=(path.replace('s3://', '')
                                                     if self.onS3
                                                     else self.path),
                                             schema=None,
                                             format='parquet',
                                             filesystem=(S3FileSystem(region=awsRegion,
                                                                      access_key=accessKey,
                                                                      secret_key=secretKey)
                                                         if self.onS3
                                                         else LocalFileSystem()),
                                             partitioning=None,
                                             partition_base_dir=None,
                                             exclude_invalid_files=None,
                                             ignore_prefixes=None)

                if verbose:
                    toc: float = time.time()
                    logger.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')

                if _filePaths := _cache._srcArrowDS.files:
                    _cache.filePaths = {(f's3://{filePath}' if self.onS3 else filePath)
                                        for filePath in _filePaths
                                        if not filePath.endswith('_$folder$')}
                    _cache.nFiles = len(_cache.filePaths)

                else:
                    _cache.nFiles = 1
                    _cache.filePaths = {self.path}

            _cache.srcColsInclPartitionKVs = set()
            _cache.srcTypesInclPartitionKVs = Namespace()

            for i, filePath in enumerate(_cache.filePaths):
                if filePath in self._FILE_CACHES:
                    fileCache: Namespace = self._FILE_CACHES[filePath]

                    if (fileCache.nRows is None) and (i < self._SCHEMA_MIN_N_FILES):
                        fileCache.localPath = self.fileLocalPath(filePath=filePath)

                        schema: Schema = read_schema(where=fileCache.localPath)

                        fileCache.srcColsExclPartitionKVs = (set(schema.names)
                                                             - {'__index_level_0__'})

                        fileCache.srcColsInclPartitionKVs.update(fileCache.srcColsExclPartitionKVs)

                        for col in (fileCache.srcColsExclPartitionKVs
                                    .difference(fileCache.partitionKVs)):
                            fileCache.srcTypesExclPartitionKVs[col] = \
                                fileCache.srcTypesInclPartitionKVs[col] = \
                                schema.field(col).type

                        metadata: FileMetaData = read_metadata(where=fileCache.localPath)
                        fileCache.nCols = metadata.num_columns
                        fileCache.nRows = metadata.num_rows

                else:
                    srcColsInclPartitionKVs: Set[str] = set()

                    srcTypesExclPartitionKVs: Namespace = Namespace()
                    srcTypesInclPartitionKVs: Namespace = Namespace()

                    partitionKVs: Dict[str, Union[datetime.date, str]] = {}

                    for partitionKV in re.findall(pattern='[^/]+=[^/]+/', string=filePath):
                        k, v = partitionKV.split(sep='=', maxsplit=1)

                        srcColsInclPartitionKVs.add(k)

                        if k == self._DATE_COL:
                            srcTypesInclPartitionKVs[k] = _ARROW_DATE_TYPE
                            partitionKVs[k] = datetime.datetime.strptime(v[:-1], '%Y-%m-%d').date()

                        else:
                            srcTypesInclPartitionKVs[k] = _ARROW_STR_TYPE
                            partitionKVs[k] = v[:-1]

                    if i < self._SCHEMA_MIN_N_FILES:
                        localPath: Path = self.fileLocalPath(filePath=filePath)

                        schema: Schema = read_schema(where=localPath)

                        srcColsExclPartitionKVs: Set[str] = (set(schema.names)
                                                             - {'__index_level_0__'})

                        srcColsInclPartitionKVs.update(srcColsExclPartitionKVs)

                        for col in srcColsExclPartitionKVs.difference(partitionKVs):
                            srcTypesExclPartitionKVs[col] = \
                                srcTypesInclPartitionKVs[col] = \
                                schema.field(col).type

                        metadata: FileMetaData = read_metadata(where=localPath)
                        nCols: int = metadata.num_columns
                        nRows: int = metadata.num_rows

                    else:
                        localPath: Optional[Path] = None if self.onS3 else filePath

                        srcColsExclPartitionKVs: Optional[Set[str]] = None

                        nCols: Optional[int] = None
                        nRows: Optional[int] = None

                    self._FILE_CACHES[filePath] = fileCache = \
                        Namespace(localPath=localPath,

                                  partitionKVs=partitionKVs,

                                  srcColsExclPartitionKVs=srcColsExclPartitionKVs,
                                  srcColsInclPartitionKVs=srcColsInclPartitionKVs,

                                  srcTypesExclPartitionKVs=srcTypesExclPartitionKVs,
                                  srcTypesInclPartitionKVs=srcTypesInclPartitionKVs,

                                  nCols=nCols, nRows=nRows)

                _cache.srcColsInclPartitionKVs |= fileCache.srcColsInclPartitionKVs

                for col, arrowType in fileCache.srcTypesInclPartitionKVs.items():
                    if col in _cache.srcTypesInclPartitionKVs:
                        assert arrowType == _cache.srcTypesInclPartitionKVs[col], \
                            TypeError(f'*** {filePath} COLUMN {col}: '
                                      f'DETECTED TYPE {arrowType} != '
                                      f'{_cache.srcTypesInclPartitionKVs[col]} ***')
                    else:
                        _cache.srcTypesInclPartitionKVs[col] = arrowType

            _cache.cachedLocally = False

        self.__dict__.update(_cache)

        self._mappers: Tuple[callable] = (()
                                          if _mappers is None
                                          else to_iterable(_mappers, iterable_type=tuple))

        self._reduceMustInclCols: Set[str] = (set()
                                              if _reduceMustInclCols is None
                                              else to_iterable(_reduceMustInclCols,
                                                               iterable_type=set))

        # extract standard keyword arguments
        self._extractStdKwArgs(kwargs, resetToClassDefaults=True, inplace=True)

        # organize time series if applicable
        self._organizeIndexCols()

        # set profiling settings and create empty profiling cache
        self._emptyCache()

    # ===========
    # STRING REPR
    # -----------
    # __repr__
    # __shortRepr__

    def __repr__(self) -> str:
        """Return string repr."""
        colAndTypeStrs: List[str] = []

        if self._iCol:
            colAndTypeStrs.append(f'(iCol) {self._iCol}: {self.type(self._iCol)}')

        if self._dCol:
            colAndTypeStrs.append(f'(dCol) {self._dCol}: {self.type(self._dCol)}')

        if self._tCol:
            colAndTypeStrs.append(f'(tCol) {self._tCol}: {self.type(self._tCol)}')

        colAndTypeStrs.extend(f'{col}: {self.type(col)}' for col in self.contentCols)

        return (f'{self.nFiles:,}-file ' +
                (f'{self._cache.nRows:,}-row '
                 if self._cache.nRows
                 else (f'approx-{self._cache.approxNRows:,.0f}-row '
                       if self._cache.approxNRows
                       else '')) +
                type(self).__name__ +
                (f'[{self.path} + {len(self._mappers):,} transform(s)]'
                 f"[{', '.join(colAndTypeStrs)}]"))

    @property
    def __shortRepr__(self) -> str:
        """Short string repr."""
        colsDescStr: List[str] = []

        if self._iCol:
            colsDescStr.append(f'iCol: {self._iCol}')

        if self._dCol:
            colsDescStr.append(f'dCol: {self._dCol}')

        if self._tCol:
            colsDescStr.append(f'tCol: {self._tCol}')

        colsDescStr.append(f'{len(self.contentCols)} content col(s)')

        return (f'{self.nFiles:,}-file ' +
                (f'{self._cache.nRows:,}-row '
                 if self._cache.nRows
                 else (f'approx-{self._cache.approxNRows:,.0f}-row '
                       if self._cache.approxNRows
                       else '')) +
                type(self).__name__ +
                (f'[{self.path} + {len(self._mappers):,} transform(s)]'
                 f"[{', '.join(colsDescStr)}]"))

    # ================================
    # "INTERNAL / DON'T TOUCH" METHODS
    # --------------------------------
    # _extractStdKwArgs

    # pylint: disable=inconsistent-return-statements
    def _extractStdKwArgs(self, kwargs: Dict[str, Any], /, *,
                          resetToClassDefaults: bool = False,
                          inplace: bool = False) -> Optional[Namespace]:
        namespace: Union[ParquetDataset, Namespace] = self if inplace else Namespace()

        for k, classDefaultV in self._DEFAULT_KWARGS.items():
            _privateK: str = f'_{k}'

            if not resetToClassDefaults:
                existingInstanceV: Any = getattr(self, _privateK, None)

            v: Any = kwargs.pop(k,
                                existingInstanceV
                                if (not resetToClassDefaults) and existingInstanceV
                                else classDefaultV)

            if (k == 'reprSampleMinNFiles') and (v > self.nFiles):
                v: int = self.nFiles

            setattr(namespace,
                    _privateK   # use _k to not invoke @k.setter right away
                    if inplace
                    else k,
                    v)

        if inplace:
            if self._iCol not in self.columns:
                self._iCol: Optional[str] = None

            if self._tCol not in self.columns:
                self._tCol: Optional[str] = None

        else:
            return namespace

    # =======
    # CACHING
    # -------
    # _emptyCache
    # _inheritCache
    # cacheLocally
    # fileLocalPath
    # cacheFileMetadataAndSchema

    def _emptyCache(self):
        self._cache: Namespace = \
            Namespace(prelimReprSampleFilePaths=None,
                      reprSampleFilePaths=None,
                      reprSample=None,

                      approxNRows=None, nRows=None,

                      count={}, distinct={},

                      nonNullProportion={},
                      suffNonNullProportionThreshold={}, suffNonNull={},

                      sampleMin={}, sampleMax={},
                      sampleMean={}, sampleMedian={},

                      outlierRstMin={}, outlierRstMax={},
                      outlierRstMean={}, outlierRstMedian={})

    def _inheritCache(self, oldS3ParquetDF: ParquetDataset, /,
                      *sameCols: str, **newColToOldColMap: str):
        # pylint: disable=arguments-differ
        if oldS3ParquetDF._cache.nRows:
            if self._cache.nRows is None:
                self._cache.nRows = oldS3ParquetDF._cache.nRows
            else:
                assert self._cache.nRows == oldS3ParquetDF._cache.nRows

        if oldS3ParquetDF._cache.approxNRows and (self._cache.approxNRows is None):
            self._cache.approxNRows = oldS3ParquetDF._cache.approxNRows

        commonCols: Set[str] = self.columns.intersection(oldS3ParquetDF.columns)

        if sameCols or newColToOldColMap:
            for newCol, oldCol in newColToOldColMap.items():
                assert newCol in self.columns
                assert oldCol in oldS3ParquetDF.columns

            for sameCol in commonCols.difference(newColToOldColMap).intersection(sameCols):
                newColToOldColMap[sameCol] = sameCol

        else:
            newColToOldColMap: Dict[str, str] = {col: col for col in commonCols}

        for cacheCategory in (
                'count', 'distinct',
                'nonNullProportion', 'suffNonNullProportionThreshold', 'suffNonNull',
                'sampleMin', 'sampleMax', 'sampleMean', 'sampleMedian',
                'outlierRstMin', 'outlierRstMax', 'outlierRstMean', 'outlierRstMedian'):
            for newCol, oldCol in newColToOldColMap.items():
                if oldCol in oldS3ParquetDF._cache.__dict__[cacheCategory]:
                    self._cache.__dict__[cacheCategory][newCol] = \
                        oldS3ParquetDF._cache.__dict__[cacheCategory][oldCol]

    def cacheLocally(self, verbose: bool = True):
        """Cache files to local disk."""
        if self.onS3 and (not (_cache := self._CACHE[self.path]).cachedLocally):
            if verbose:
                self.stdOutLogger.info(msg=(msg := 'Caching Files to Local Disk...'))
                tic: float = time.time()

            parsedURL: ParseResult = urlparse(url=self.path, scheme='', allow_fragments=True)

            localPath: str = str(self._LOCAL_CACHE_DIR_PATH / parsedURL.netloc / parsedURL.path[1:])

            s3.sync(from_dir_path=self.path, to_dir_path=localPath,
                    delete=True, quiet=True, verbose=True)

            for filePath in self.filePaths:
                self._FILE_CACHES[filePath].localPath = filePath.replace(self.path, localPath)

            _cache.cachedLocally = True

            if verbose:
                toc: float = time.time()
                self.stdOutLogger.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')

    def fileLocalPath(self, filePath: str) -> Path:
        """Get local cache file path."""
        if self.onS3:
            if (filePath in self._FILE_CACHES) and self._FILE_CACHES[filePath].localPath:
                return self._FILE_CACHES[filePath].localPath

            parsedURL: ParseResult = urlparse(url=filePath, scheme='', allow_fragments=True)

            localPath: Path = self._LOCAL_CACHE_DIR_PATH / parsedURL.netloc / parsedURL.path[1:]

            localDirPath: Path = localPath.parent
            fs.mkdir(dir_path=localDirPath, hdfs=False)
            # make sure the dir has been created
            while not localDirPath.is_dir():
                time.sleep(1)

            self.s3Client.download_file(Bucket=parsedURL.netloc,
                                        Key=parsedURL.path[1:],
                                        Filename=str(localPath))
            # make sure AWS S3's asynchronous process has finished
            # downloading a potentially large file
            while not localPath.is_file():
                time.sleep(1)

            if filePath in self._FILE_CACHES:
                self._FILE_CACHES[filePath].localPath = localPath

            return localPath

        return filePath

    def cacheFileMetadataAndSchema(self, filePath: str) -> Namespace:
        """Cache file metadata and schema."""
        fileLocalPath: Path = self.fileLocalPath(filePath=filePath)

        fileCache: Namespace = self._FILE_CACHES[filePath]

        if fileCache.nRows is None:
            schema: Schema = read_schema(where=fileLocalPath)

            fileCache.srcColsExclPartitionKVs = set(schema.names) - {'__index_level_0__'}

            fileCache.srcColsInclPartitionKVs.update(fileCache.srcColsExclPartitionKVs)

            self.srcColsInclPartitionKVs.update(fileCache.srcColsExclPartitionKVs)

            for col in fileCache.srcColsExclPartitionKVs.difference(fileCache.partitionKVs):
                fileCache.srcTypesExclPartitionKVs[col] = \
                    fileCache.srcTypesInclPartitionKVs[col] = \
                    _arrowType = schema.field(col).type

                assert not is_binary(_arrowType), \
                    TypeError(f'*** {filePath}: {col} IS OF BINARY TYPE ***')

                if col in self.srcTypesInclPartitionKVs:
                    assert _arrowType == self.srcTypesInclPartitionKVs[col], \
                        TypeError(f'*** {filePath} COLUMN {col}: '
                                  f'DETECTED TYPE {_arrowType} != '
                                  f'{self.srcTypesInclPartitionKVs[col]} ***')
                else:
                    self.srcTypesInclPartitionKVs[col] = _arrowType

            metadata: FileMetaData = read_metadata(where=fileCache.localPath)
            fileCache.nCols = metadata.num_columns
            fileCache.nRows = metadata.num_rows

        return fileCache

    # =====================
    # ROWS, COLUMNS & TYPES
    # ---------------------
    # approxNRows / nRows / __len__
    # columns
    # indexCols
    # types
    # type / typeIsNum
    # possibleFeatureCols
    # possibleCatCols

    @property
    def approxNRows(self) -> int:
        """Approximate number of rows."""
        if self._cache.approxNRows is None:
            self.stdOutLogger.info(msg='Counting Approx. No. of Rows...')

            self._cache.approxNRows = (
                self.nFiles
                * sum(self.cacheFileMetadataAndSchema(filePath=filePath).nRows
                      for filePath in (tqdm(self.prelimReprSampleFilePaths)
                                       if len(self.prelimReprSampleFilePaths) > 1
                                       else self.prelimReprSampleFilePaths))
                / self._reprSampleMinNFiles)

        return self._cache.approxNRows

    @property
    def nRows(self) -> int:
        """Return number of rows."""
        if self._cache.nRows is None:
            self.stdOutLogger.info(msg='Counting No. of Rows...')

            self._cache.nRows = \
                sum(self.cacheFileMetadataAndSchema(filePath=filePath).nRows
                    for filePath in (tqdm(self.filePaths) if self.nFiles > 1 else self.filePaths))

        return self._cache.nRows

    def __len__(self) -> int:
        """Return (approximate) number of rows."""
        return self._cache.nRows if self._cache.nRows else self.approxNRows

    @property
    def columns(self) -> Set[str]:
        """Column names."""
        return self.srcColsInclPartitionKVs

    @property
    def indexCols(self) -> Set[str]:
        """Return index columns."""
        s: Set[str] = set()

        if self._iCol:
            s.add(self._iCol)

        if self._dCol:
            s.add(self._dCol)

        if self._tCol:
            s.add(self._tCol)

        return s

    @property
    def types(self) -> Namespace:
        """Return column data types."""
        return self.srcTypesInclPartitionKVs

    @lru_cache(maxsize=None, typed=False)
    def type(self, col: str) -> DataType:
        """Return data type of specified column."""
        return self.types[col]

    @lru_cache(maxsize=None, typed=False)
    def typeIsNum(self, col: str) -> bool:
        """Check whether specified column's data type is numerical."""
        return is_num(self.type(col))

    @property
    def possibleFeatureCols(self) -> Set[str]:
        """Possible feature columns for ML modeling."""
        return {col for col in self.contentCols if is_possible_feature(self.type(col))}

    @property
    def possibleCatCols(self) -> Set[str]:
        """Possible categorical content columns."""
        return {col for col in self.contentCols if is_possible_cat(self.type(col))}

    # ====================
    # MAP/REDUCE & related
    # --------------------
    # map
    # reduce
    # __getitem__
    # castType
    # collect

    def map(self, *mappers: callable,
            reduceMustInclCols: Optional[ColsType] = None,
            **kwargs: Any) -> ParquetDataset:
        """Apply mapper function(s) to files."""
        if reduceMustInclCols is None:
            reduceMustInclCols: Set[str] = set()

        inheritCache: bool = kwargs.pop('inheritCache', False)
        inheritNRows: bool = kwargs.pop('inheritNRows', inheritCache)

        s3ParquetDF: ParquetDataset = \
            ParquetDataset(
                path=self.path, awsRegion=self.awsRegion,
                accessKey=self.accessKey, secretKey=self.secretKey,

                _mappers=self._mappers + mappers,
                _reduceMustInclCols=(self._reduceMustInclCols |
                                     to_iterable(reduceMustInclCols, iterable_type=set)),

                iCol=self._iCol, tCol=self._tCol,

                reprSampleMinNFiles=self._reprSampleMinNFiles, reprSampleSize=self._reprSampleSize,

                nulls=self._nulls,
                minNonNullProportion=self._minNonNullProportion,
                outlierTailProportion=self._outlierTailProportion,
                maxNCats=self._maxNCats,
                minProportionByMaxNCats=self._minProportionByMaxNCats,

                **kwargs)

        if inheritCache:
            s3ParquetDF._inheritCache(self)

        if inheritNRows:
            s3ParquetDF._cache.approxNRows = self._cache.approxNRows
            s3ParquetDF._cache.nRows = self._cache.nRows

        return s3ParquetDF

    def reduce(self, *filePaths: str, **kwargs: Any) -> ReducedDataSetType:
        # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        """Reduce from mapped content."""
        _CHUNK_SIZE: int = 10 ** 5

        cols: Optional[Collection[str]] = kwargs.get('cols')
        cols: Set[str] = to_iterable(cols, iterable_type=set) if cols else set()

        nSamplesPerFile: int = kwargs.get('nSamplesPerFile')

        reducer: callable = kwargs.get('reducer',
                                       lambda results:
                                           vstack(tup=results)
                                           if isinstance(results[0], ndarray)
                                           else concat(objs=results,
                                                       axis='index',
                                                       join='outer',
                                                       ignore_index=False,
                                                       keys=None,
                                                       levels=None,
                                                       names=None,
                                                       verify_integrity=False,
                                                       sort=False,
                                                       copy=False))

        verbose: bool = kwargs.pop('verbose', True)

        if not filePaths:
            filePaths: Set[str] = self.filePaths

        results: List[ReducedDataSetType] = []

        # pylint: disable=too-many-nested-blocks
        for filePath in (tqdm(filePaths) if verbose and (len(filePaths) > 1) else filePaths):
            fileLocalPath: Path = self.fileLocalPath(filePath=filePath)

            fileCache: Namespace = self.cacheFileMetadataAndSchema(filePath=filePath)

            colsForFile: Set[str] = (
                cols
                if cols
                else fileCache.srcColsInclPartitionKVs
            ) | self._reduceMustInclCols

            srcCols: Set[str] = colsForFile & fileCache.srcColsExclPartitionKVs

            partitionKeyCols: Set[str] = colsForFile.intersection(fileCache.partitionKVs)

            if srcCols:
                pandasDFConstructed: bool = False

                if toSubSample := nSamplesPerFile and (nSamplesPerFile < fileCache.nRows):
                    intermediateN: float = (nSamplesPerFile * fileCache.nRows) ** .5

                    if ((nChunksForIntermediateN := int(math.ceil(intermediateN / _CHUNK_SIZE)))
                            < (approxNChunks := int(math.ceil(fileCache.nRows / _CHUNK_SIZE)))):
                        # arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table
                        fileArrowTable: Table = read_table(source=fileLocalPath,
                                                           columns=list(srcCols),
                                                           use_threads=True,
                                                           metadata=None,
                                                           use_pandas_metadata=True,
                                                           memory_map=False,
                                                           read_dictionary=None,
                                                           filesystem=None,
                                                           filters=None,
                                                           buffer_size=0,
                                                           partitioning='hive',
                                                           use_legacy_dataset=False,
                                                           ignore_prefixes=None,
                                                           pre_buffer=True,
                                                           coerce_int96_timestamp_unit=None)

                        chunkRecordBatches: List[RecordBatch] = \
                            fileArrowTable.to_batches(max_chunksize=_CHUNK_SIZE)

                        nChunks: int = len(chunkRecordBatches)

                        # TODO: CHECK
                        # assert nChunks in (approxNChunks - 1, approxNChunks), \
                        #     ValueError(f'*** {filePath}: {nChunks} vs. '
                        #                f'{approxNChunks} Record Batches ***')

                        assert nChunksForIntermediateN <= nChunks, \
                            ValueError(f'*** {filePath}: {nChunksForIntermediateN} vs. '
                                       f'{nChunks} Record Batches ***')

                        chunkPandasDFs: List[DataFrame] = []

                        nSamplesPerChunk: int = int(math.ceil(nSamplesPerFile /
                                                              nChunksForIntermediateN))

                        for chunkRecordBatch in randomSample(population=chunkRecordBatches,
                                                             sampleSize=nChunksForIntermediateN,
                                                             returnCollectionType=tuple):
                            # arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html
                            # #pyarrow.RecordBatch.to_pandas
                            chunkPandasDF: DataFrame = \
                                chunkRecordBatch.to_pandas(
                                    memory_pool=None,
                                    categories=None,
                                    strings_to_categorical=False,
                                    zero_copy_only=False,

                                    integer_object_nulls=False,
                                    # TODO: check
                                    # (bool, default False) –
                                    # Cast integers with nulls to objects

                                    date_as_object=True,
                                    # TODO: check
                                    # (bool, default True) –
                                    # Cast dates to objects.
                                    # If False, convert to datetime64[ns] dtype.

                                    timestamp_as_object=False,
                                    use_threads=True,

                                    deduplicate_objects=True,
                                    # TODO: check
                                    # (bool, default False) –
                                    # Do not create multiple copies Python objects when created,
                                    # to save on memory use. Conversion will be slower.

                                    ignore_metadata=False,
                                    safe=True,

                                    split_blocks=True,
                                    # TODO: check
                                    # (bool, default False) –
                                    # If True, generate one internal “block”
                                    # for each column when creating a pandas.DataFrame
                                    # from a RecordBatch or Table.
                                    # While this can temporarily reduce memory
                                    # note that various pandas operations can
                                    # trigger “consolidation” which may balloon memory use.

                                    self_destruct=True,
                                    # TODO: check
                                    # EXPERIMENTAL: If True, attempt to deallocate
                                    # the originating Arrow memory while
                                    # converting the Arrow object to pandas.
                                    # If you use the object after calling to_pandas
                                    # with this option it will crash your program.
                                    # Note that you may not see always memory usage improvements.
                                    # For example, if multiple columns share
                                    # an underlying allocation, memory can’t be freed
                                    # until all columns are converted.

                                    types_mapper=None)

                            for k in partitionKeyCols:
                                chunkPandasDF[k] = fileCache.partitionKVs[k]

                            if nSamplesPerChunk < len(chunkPandasDF):
                                chunkPandasDF: DataFrame = \
                                    chunkPandasDF.sample(n=nSamplesPerChunk,
                                                         # frac=None,
                                                         replace=False,
                                                         weights=None,
                                                         random_state=None,
                                                         axis='index',
                                                         ignore_index=False)

                            chunkPandasDFs.append(chunkPandasDF)

                        filePandasDF: DataFrame = concat(objs=chunkPandasDFs,
                                                         axis='index',
                                                         join='outer',
                                                         ignore_index=False,
                                                         keys=None,
                                                         levels=None,
                                                         names=None,
                                                         verify_integrity=False,
                                                         sort=False,
                                                         copy=False)

                        pandasDFConstructed: bool = True

                if not pandasDFConstructed:
                    # pandas.pydata.org/docs/reference/api/pandas.read_parquet
                    filePandasDF: DataFrame = read_parquet(
                        path=fileLocalPath,
                        engine='pyarrow',
                        columns=list(srcCols),
                        storage_options=None,
                        use_nullable_dtypes=True,

                        # arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table:
                        use_threads=True,
                        metadata=None,
                        use_pandas_metadata=True,
                        memory_map=False,
                        read_dictionary=None,
                        filesystem=None,
                        filters=None,
                        buffer_size=0,
                        partitioning='hive',
                        use_legacy_dataset=False,
                        ignore_prefixes=None,
                        pre_buffer=True,
                        coerce_int96_timestamp_unit=None,

                        # arrow.apache.org/docs/python/generated/pyarrow.Table.html
                        # #pyarrow.Table.to_pandas:
                        # memory_pool=None,   # (default)
                        # categories=None,   # (default)
                        # strings_to_categorical=False,   # (default)
                        # zero_copy_only=False,   # (default)

                        # integer_object_nulls=False,   # (default)
                        # TODO: check
                        # (bool, default False) –
                        # Cast integers with nulls to objects

                        # date_as_object=True,   # (default)
                        # TODO: check
                        # (bool, default True) –
                        # Cast dates to objects.
                        # If False, convert to datetime64[ns] dtype.

                        # timestamp_as_object=False,   # (default)
                        # use_threads=True,   # (default)

                        # deduplicate_objects=True,   # (default: *** False ***)
                        # TODO: check
                        # (bool, default False) –
                        # Do not create multiple copies Python objects when created,
                        # to save on memory use. Conversion will be slower.

                        # ignore_metadata=False,   # (default)
                        # safe=True,   # (default)

                        # split_blocks=True,   # (default: *** False ***)
                        # TODO: check
                        # (bool, default False) –
                        # If True, generate one internal “block” for each column
                        # when creating a pandas.DataFrame from a RecordBatch or Table.
                        # While this can temporarily reduce memory note that
                        # various pandas operations can trigger “consolidation”
                        # which may balloon memory use.

                        # self_destruct=True,   # (default: *** False ***)
                        # TODO: check
                        # EXPERIMENTAL: If True, attempt to deallocate the originating
                        # Arrow memory while converting the Arrow object to pandas.
                        # If you use the object after calling to_pandas with this option
                        # it will crash your program.
                        # Note that you may not see always memory usage improvements.
                        # For example, if multiple columns share an underlying allocation,
                        # memory can’t be freed until all columns are converted.

                        # types_mapper=None,   # (default)
                    )

                    for k in partitionKeyCols:
                        filePandasDF[k] = fileCache.partitionKVs[k]

                    if toSubSample:
                        filePandasDF: DataFrame = filePandasDF.sample(n=nSamplesPerFile,
                                                                      # frac=None,
                                                                      replace=False,
                                                                      weights=None,
                                                                      random_state=None,
                                                                      axis='index',
                                                                      ignore_index=False)

            else:
                filePandasDF: DataFrame = DataFrame(index=range(nSamplesPerFile
                                                                if nSamplesPerFile and
                                                                (nSamplesPerFile < fileCache.nRows)
                                                                else fileCache.nRows))

                for k in partitionKeyCols:
                    filePandasDF[k] = fileCache.partitionKVs[k]

            result: ReducedDataSetType = filePandasDF
            for mapper in self._mappers:
                result: ReducedDataSetType = mapper(result)

            results.append(result)

        return reducer(results)

    @staticmethod
    def _getCols(pandasDF: DataFrame, cols: Union[str, Tuple[str]]) -> DataFrame:
        for missingCol in to_iterable(cols, iterable_type=set).difference(pandasDF.columns):
            pandasDF.loc[:, missingCol] = None

        return pandasDF[cols if isinstance(cols, str) else list(cols)]

    @lru_cache(maxsize=None, typed=False)
    def __getitem__(self, cols: Union[str, Tuple[str]], /) -> ParquetDataset:
        """Get column(s)."""
        return self.map(partial(self._getCols, cols=cols),
                        reduceMustInclCols=cols,
                        inheritNRows=True)

    @lru_cache(maxsize=None, typed=False)
    def castType(self, **colsToTypes: Dict[str, Any]) -> ParquetDataset:
        """Cast data type(s) of column(s)."""
        return self.map(lambda df: df.astype(colsToTypes, copy=False, errors='raise'),
                        reduceMustInclCols=set(colsToTypes),
                        inheritNRows=True)

    def collect(self, *cols: str, **kwargs: Any) -> ReducedDataSetType:
        """Collect content."""
        return self.reduce(cols=cols if cols else None, **kwargs)

    # =========
    # FILTERING
    # ---------
    # _subset
    # filterByPartitionKeys
    # filter

    @lru_cache(maxsize=None, typed=False)   # computationally expensive, so cached
    def _subset(self, *filePaths: str, **kwargs: Any) -> ParquetDataset:
        # pylint: disable=too-many-locals
        if filePaths:
            assert self.filePaths.issuperset(filePaths)

            nFilePaths: int = len(filePaths)

            if nFilePaths == self.nFiles:
                return self

            if nFilePaths > 1:
                verbose: bool = kwargs.pop('verbose', True)

                _pathPlusSepLen: int = len(self.path) + 1
                fileSubPaths: List[str] = [filePath[_pathPlusSepLen:] for filePath in filePaths]

                _uuid = uuid4()
                subsetPath: str = (
                    f"s3://{self.s3Bucket}/{(subsetDirS3Key := f'{self._TMP_DIR_S3_KEY}/{_uuid}')}"
                    if self.onS3
                    else f'{self._LOCAL_CACHE_DIR_PATH}/{_uuid}')

                if verbose:
                    self.stdOutLogger.info(
                        msg=(msg := f'Subsetting {len(filePaths):,} Files to "{subsetPath}"...'))
                    tic: float = time.time()

                for fileSubPath in (tqdm(fileSubPaths) if verbose else fileSubPaths):
                    if self.onS3:
                        self.s3Client.copy(CopySource=dict(Bucket=self.s3Bucket,
                                                           Key=f'{self.pathS3Key}/{fileSubPath}'),
                                           Bucket=self.s3Bucket,
                                           Key=f'{subsetDirS3Key}/{fileSubPath}')
                    else:
                        fs.cp(from_path=f'{self.path}/{fileSubPath}',
                              to_path=f'{subsetPath}/{fileSubPath}',
                              hdfs=False, is_dir=False)

                if verbose:
                    toc: float = time.time()
                    self.stdOutLogger.info(msg=f'{msg} done!   <{toc-tic:.1f} s>')

            else:
                subsetPath: str = filePaths[0]

            return ParquetDataset(
                path=subsetPath, awsRegion=self.awsRegion,
                accessKey=self.accessKey, secretKey=self.secretKey,

                _mappers=self._mappers, _reduceMustInclCols=self._reduceMustInclCols,

                iCol=self._iCol, tCol=self._tCol,

                reprSampleMinNFiles=self._reprSampleMinNFiles, reprSampleSize=self._reprSampleSize,

                nulls=self._nulls,
                minNonNullProportion=self._minNonNullProportion,
                outlierTailProportion=self._outlierTailProportion,
                maxNCats=self._maxNCats,
                minProportionByMaxNCats=self._minProportionByMaxNCats,

                **kwargs)

        return self

    @lru_cache(maxsize=None, typed=False)
    def filterByPartitionKeys(self,
                              *filterCriteriaTuples: Union[Tuple[str, str], Tuple[str, str, str]],
                              **kwargs: Any) -> ParquetDataset:
        # pylint: disable=too-many-branches
        """Filter by partition keys."""
        filterCriteria: Dict[str, Tuple[Optional[str], Optional[str], Optional[Set[str]]]] = {}

        _samplePath: str = next(iter(self.filePaths))

        for filterCriteriaTuple in filterCriteriaTuples:
            assert isinstance(filterCriteriaTuple, PY_LIST_OR_TUPLE)
            filterCriteriaTupleLen: int = len(filterCriteriaTuple)

            col: str = filterCriteriaTuple[0]

            if f'{col}=' in _samplePath:
                if filterCriteriaTupleLen == 2:
                    fromVal: Optional[str] = None
                    toVal: Optional[str] = None
                    inSet: Set[str] = {str(v) for v in to_iterable(filterCriteriaTuple[1])}

                elif filterCriteriaTupleLen == 3:
                    fromVal: Optional[str] = filterCriteriaTuple[1]
                    if fromVal is not None:
                        fromVal: str = str(fromVal)

                    toVal: Optional[str] = filterCriteriaTuple[2]
                    if toVal is not None:
                        toVal: str = str(toVal)

                    inSet: Optional[Set[str]] = None

                else:
                    raise ValueError(f'*** {type(self)} FILTER CRITERIA MUST BE EITHER '
                                     '(<colName>, <fromVal>, <toVal>) OR '
                                     '(<colName>, <inValsSet>) ***')

                filterCriteria[col] = fromVal, toVal, inSet

        if filterCriteria:
            filePaths: Set[str] = set()

            for filePath in self.filePaths:
                filePandasDFSatisfiesCriteria: bool = True

                for col, (fromVal, toVal, inSet) in filterCriteria.items():
                    v: str = re.search(f'{col}=(.*?)/', filePath).group(1)

                    # pylint: disable=too-many-boolean-expressions
                    if ((fromVal is not None) and (v < fromVal)) or \
                            ((toVal is not None) and (v > toVal)) or \
                            ((inSet is not None) and (v not in inSet)):
                        filePandasDFSatisfiesCriteria: bool = False
                        break

                if filePandasDFSatisfiesCriteria:
                    filePaths.add(filePath)

            assert filePaths, FileNotFoundError(f'*** {self}: NO  PATHS SATISFYING '
                                                f'FILTER CRITERIA {filterCriteria} ***')

            return self._subset(*filePaths, **kwargs)

        return self

    @lru_cache(maxsize=None, typed=False)
    def filter(self, *conditions: str, **kwargs: Any) -> ParquetDataset:
        """Apply filtering mapper."""
        s3ParquetDF: ParquetDataset = self

        for condition in conditions:
            # pylint: disable=cell-var-from-loop
            s3ParquetDF: ParquetDataset = \
                s3ParquetDF.map(lambda df: df.query(expr=condition, inplace=False),
                                **kwargs)

        return s3ParquetDF

    # ========
    # SAMPLING
    # --------
    # prelimReprSampleFilePaths
    # reprSampleFilePaths
    # sample
    # _assignReprSample

    @property
    def prelimReprSampleFilePaths(self) -> Set[str]:
        """Prelim representative sample file paths."""
        if self._cache.prelimReprSampleFilePaths is None:
            self._cache.prelimReprSampleFilePaths = \
                randomSample(population=self.filePaths,
                             sampleSize=self._reprSampleMinNFiles)

        return self._cache.prelimReprSampleFilePaths

    @property
    def reprSampleFilePaths(self) -> Set[str]:
        """Return representative sample file paths."""
        if self._cache.reprSampleFilePaths is None:
            reprSampleNFiles: int = \
                int(math.ceil(
                    ((min(self._reprSampleSize, self.approxNRows) / self.approxNRows) ** .5)
                    * self.nFiles))

            self._cache.reprSampleFilePaths = (
                self._cache.prelimReprSampleFilePaths |
                (randomSample(
                    population=self.filePaths - self._cache.prelimReprSampleFilePaths,
                    sampleSize=reprSampleNFiles - self._reprSampleMinNFiles)
                 if reprSampleNFiles > self._reprSampleMinNFiles
                 else set()))

        return self._cache.reprSampleFilePaths

    def sample(self, *cols: str, **kwargs: Any) -> ReducedDataSetType:
        """Sample."""
        n: int = kwargs.pop('n', self._DEFAULT_REPR_SAMPLE_SIZE)

        filePaths: Optional[Collection[str]] = kwargs.pop('filePaths', None)

        verbose: bool = kwargs.pop('verbose', True)

        if filePaths:
            nFiles: int = len(filePaths)

        else:
            minNFiles: int = kwargs.pop('minNFiles', self._reprSampleMinNFiles)
            maxNFiles: Optional[int] = kwargs.pop('maxNFiles', None)

            nFiles: int = (max(int(math.ceil(((min(n, self.approxNRows) / self.approxNRows) ** .5)
                                             * self.nFiles)),
                               minNFiles)
                           if (self.nFiles > 1) and ((maxNFiles is None) or (maxNFiles > 1))
                           else 1)

            if maxNFiles:
                nFiles: int = min(nFiles, maxNFiles)

            if nFiles < self.nFiles:
                filePaths: Set[str] = randomSample(population=self.filePaths, sampleSize=nFiles)
            else:
                nFiles: int = self.nFiles
                filePaths: Set[str] = self.filePaths

        if verbose or debug.ON:
            self.stdOutLogger.info(
                msg=f"Sampling {n:,} Rows{f' of Columns {cols}' if cols else ''} "
                    f'from {nFiles:,} Files...')

        return self.reduce(*filePaths,
                           cols=cols,
                           nSamplesPerFile=int(math.ceil(n / nFiles)),
                           verbose=verbose,
                           **kwargs)

    def _assignReprSample(self):
        self._cache.reprSample = self.sample(n=self._reprSampleSize,
                                             filePaths=self.reprSampleFilePaths,
                                             verbose=True)

        # pylint: disable=attribute-defined-outside-init
        self._reprSampleSize: int = len(self._cache.reprSample)

        self._cache.nonNullProportion = {}
        self._cache.suffNonNull = {}

    # ================
    # COLUMN PROFILING
    # ----------------
    # count
    # nonNullProportion
    # distinct
    # distinctPartitions
    # quantile
    # sampleStat
    # outlierRstStat / outlierRstMin / outlierRstMax
    # profile

    def count(self, *cols: str, **kwargs: Any) -> Union[int, Namespace]:
        """Count non-NULL values in specified column(s).

        Return:
            - If 1 column name is given,
            return its corresponding non-``NULL`` count

            - If multiple column names are given,
            return a {``col``: corresponding non-``NULL`` count} *dict*

            - If no column names are given,
            return a {``col``: corresponding non-``NULL`` count} *dict*
            for all columns
        """
        if not cols:
            cols: Set[str] = self.contentCols

        if len(cols) > 1:
            return Namespace(**{col: self.count(col, **kwargs) for col in cols})

        col: str = cols[0]

        pandasDF: Optional[DataFrame] = kwargs.get('pandasDF')

        lowerNumericNull, upperNumericNull = self._nulls[col]

        if pandasDF is None:
            if col not in self._cache.count:
                verbose: Optional[bool] = True if debug.ON else kwargs.get('verbose')

                if verbose:
                    tic: float = time.time()

                self._cache.count[col] = result = int(
                    self[col]
                    .map(((lambda series: (series.notnull()
                                           .sum(axis='index',
                                                skipna=True,
                                                level=None,
                                                # numeric_only=True,
                                                min_count=0)))

                          if isnull(upperNumericNull)

                          else (lambda series: ((series < upperNumericNull)
                                                .sum(axis='index',
                                                     skipna=True,
                                                     level=None,
                                                     # numeric_only=True,
                                                     min_count=0))))

                         if isnull(lowerNumericNull)

                         else ((lambda series: ((series > lowerNumericNull)
                                                .sum(axis='index',
                                                     skipna=True,
                                                     level=None,
                                                     # numeric_only=True,
                                                     min_count=0)))

                               if isnull(upperNumericNull)

                               else (lambda series: (series
                                                     .between(left=lowerNumericNull,
                                                              right=upperNumericNull,
                                                              inclusive='neither')
                                                     .sum(axis='index',
                                                          skipna=True,
                                                          level=None,
                                                          # numeric_only=True,
                                                          min_count=0)))),
                         reduceMustInclCols=col)
                    .reduce(cols=col, reducer=sum))

                if verbose:
                    toc: float = time.time()
                    self.stdOutLogger.info(msg=f'No. of Non-NULLs of Column "{col}" = '
                                               f'{result:,}   <{toc - tic:,.1f} s>')

            return self._cache.count[col]

        series: Series = pandasDF[col]

        series: Series = ((series.notnull()

                           if isnull(upperNumericNull)

                           else (series < upperNumericNull))

                          if isnull(lowerNumericNull)

                          else ((series > lowerNumericNull)

                                if isnull(upperNumericNull)

                                else series.between(left=lowerNumericNull,
                                                    right=upperNumericNull,
                                                    inclusive='neither')))

        return series.sum(axis='index',
                          skipna=True,
                          level=None,
                          # numeric_only=True,
                          min_count=0)

    def nonNullProportion(self, *cols: str, **kwargs: Any) -> Union[float, Namespace]:
        """Calculate non-NULL data proportion(s) of specified column(s).

        Return:
            - If 1 column name is given,
            return its *approximate* non-``NULL`` proportion

            - If multiple column names are given,
            return {``col``: approximate non-``NULL`` proportion} *dict*

            - If no column names are given,
            return {``col``: approximate non-``NULL`` proportion}
            *dict* for all columns
        """
        if not cols:
            cols: Set[str] = self.contentCols

        if len(cols) > 1:
            return Namespace(**{col: self.nonNullProportion(col, **kwargs) for col in cols})

        col: str = cols[0]

        if col not in self._cache.nonNullProportion:
            self._cache.nonNullProportion[col] = (
                self.count(col, pandasDF=self.reprSample, **kwargs) /
                self.reprSampleSize)

        return self._cache.nonNullProportion[col]

    def distinct(self, *cols: str, **kwargs: Any) -> Union[Series, Namespace]:
        """Return distinct values in specified column(s).

        Return:
            *Approximate* list of distinct values of ``ADF``'s column ``col``,
                with optional descending-sorted counts for those values

        Args:
            col (str): name of a column

            count (bool): whether to count the number of appearances
            of each distinct value of the specified ``col``
        """
        if not cols:
            cols: Set[str] = self.contentCols

        asDict: bool = kwargs.pop('asDict', False)

        if len(cols) > 1:
            return Namespace(**{col: self.distinct(col, **kwargs) for col in cols})

        col: str = cols[0]

        if col not in self._cache.distinct:
            self._cache.distinct[col] = \
                self.reprSample[col].value_counts(normalize=True,
                                                  sort=True,
                                                  ascending=False,
                                                  bins=None,
                                                  dropna=False)

        return (Namespace(**{col: self._cache.distinct[col]})
                if asDict
                else self._cache.distinct[col])

    def distinctPartitions(self, col: str, /) -> Set[str]:
        """Return distinct values of a certain partition key."""
        return {re.search(f'{col}=(.*?)/', filePath).group(1)
                for filePath in self.filePaths}

    @lru_cache(maxsize=None, typed=False)   # computationally expensive, so cached
    def quantile(self, *cols: str, **kwargs: Any) -> Union[float, int,
                                                           Series, Namespace]:
        """Return quantile values in specified column(s)."""
        if len(cols) > 1:
            return Namespace(**{col: self.quantile(col, **kwargs) for col in cols})

        col: str = cols[0]

        # for precision, calc from whole data set instead of from reprSample
        return self[col].reduce(cols=col).quantile(q=kwargs.get('q', .5),
                                                   interpolation='linear')

    def sampleStat(self, *cols: str, **kwargs: Any) -> Union[float, int, Namespace]:
        """Approximate measurements of a certain stat on numerical columns.

        Args:
            *cols (str): column name(s)
            **kwargs:
                - **stat**: one of the following:
                    - ``avg``/``mean`` (default)
                    - ``median``
                    - ``min``
                    - ``max``
        """
        if not cols:
            cols: Set[str] = self.possibleNumCols

        if len(cols) > 1:
            return Namespace(**{col: self.sampleStat(col, **kwargs) for col in cols})

        col: str = cols[0]

        if self.typeIsNum(col):
            stat: str = kwargs.pop('stat', 'mean').lower()
            if stat == 'avg':
                stat: str = 'mean'
            capitalizedStatName: str = stat.capitalize()
            s: str = f'sample{capitalizedStatName}'

            if s not in self._cache:
                setattr(self._cache, s, {})
            _cache: Dict[str, PyNumType] = getattr(self._cache, s)

            if col not in _cache:
                verbose: Optional[bool] = True if debug.ON else kwargs.get('verbose')

                if verbose:
                    tic: float = time.time()

                result = getattr(self.reprSample[col], stat)(axis='index', skipna=True, level=None)

                if isinstance(result, NUMPY_FLOAT_TYPES):
                    result: float = float(result)

                elif isinstance(result, NUMPY_INT_TYPES):
                    result: int = int(result)

                assert isinstance(result, PY_NUM_TYPES + (NAType,)), \
                    TypeError(f'*** "{col}" SAMPLE '
                              f'{capitalizedStatName.upper()} = '
                              f'{result} ({type(result)}) ***')

                if verbose:
                    toc: float = time.time()
                    self.stdOutLogger.info(msg=f'Sample {capitalizedStatName} for Column "{col}" = '
                                               f'{result:,.3g}   <{toc - tic:,.1f} s>')

                _cache[col] = result

            return _cache[col]

        raise ValueError(f'*** {self}.sampleStat({col}, ...): COLUMN "{col}" NOT NUMERICAL ***')

    def outlierRstStat(self, *cols: str, **kwargs: Any) -> Union[float, int, Namespace]:
        # pylint: disable=too-many-branches
        """Return outlier-resistant stat for specified column(s)."""
        if not cols:
            cols: Set[str] = self.possibleNumCols

        if len(cols) > 1:
            return Namespace(**{col: self.outlierRstStat(col, **kwargs) for col in cols})

        col: str = cols[0]

        if self.typeIsNum(col):
            stat: str = kwargs.pop('stat', 'mean').lower()
            if stat == 'avg':
                stat: str = 'mean'
            capitalizedStatName: str = stat.capitalize()
            s: str = f'outlierRst{capitalizedStatName}'

            if hasattr(self, s):
                return getattr(self, s)(col, **kwargs)

            if s not in self._cache:
                setattr(self._cache, s, {})
            _cache: Dict[str, PyNumType] = getattr(self._cache, s)

            if col not in _cache:
                verbose: Optional[bool] = True if debug.ON else kwargs.get('verbose')

                if verbose:
                    tic: float = time.time()

                series: Series = self.reprSample[col]

                outlierTail: Optional[str] = kwargs.pop('outlierTail', 'both')

                if outlierTail == 'both':
                    series: Series = series.loc[
                        series.between(left=self.outlierRstMin(col),
                                       right=self.outlierRstMax(col),
                                       inclusive='both')]

                elif outlierTail == 'lower':
                    series: Series = series.loc[series >= self.outlierRstMin(col)]

                elif outlierTail == 'upper':
                    series: Series = series.loc[series <= self.outlierRstMax(col)]

                result = getattr(series, stat)(axis='index', skipna=True, level=None)

                if isnull(result):
                    self.stdOutLogger.warning(
                        msg=f'*** "{col}" OUTLIER-RESISTANT '
                            f'{capitalizedStatName.upper()} = '
                            f'{result} ***')

                    result: PyNumType = self.outlierRstMin(col)

                if isinstance(result, NUMPY_FLOAT_TYPES):
                    result: float = float(result)

                elif isinstance(result, NUMPY_INT_TYPES):
                    result: int = int(result)

                assert isinstance(result, PY_NUM_TYPES + (NAType,)), \
                    TypeError(f'*** "{col}" '
                              f'OUTLIER-RESISTANT {capitalizedStatName.upper()}'
                              f' = {result} ({type(result)}) ***')

                if verbose:
                    toc: float = time.time()
                    self.stdOutLogger.info(msg=f'Outlier-Resistant {capitalizedStatName}'
                                               f' for Column "{col}" = '
                                               f'{result:,.3g}   <{toc - tic:,.1f} s>')

                _cache[col] = result

            return _cache[col]

        raise ValueError(f'*** {self}.outlierRstStat({col}, ...): '
                         f'COLUMN "{col}" NOT NUMERICAL ***')

    def outlierRstMin(self, *cols: str, **kwargs: Any) -> Union[float, int, Namespace]:
        """Return outlier-resistant minimum for specified column(s)."""
        if not cols:
            cols: Set[str] = self.possibleNumCols

        if len(cols) > 1:
            return Namespace(**{col: self.outlierRstMin(col, **kwargs) for col in cols})

        col: str = cols[0]

        if self.typeIsNum(col):
            if 'outlierRstMin' not in self._cache:
                self._cache.outlierRstMin = {}

            if col not in self._cache.outlierRstMin:
                verbose: Optional[bool] = True if debug.ON else kwargs.get('verbose')

                if verbose:
                    tic: float = time.time()

                series: Series = self.reprSample[col]

                outlierRstMin: PyNumType = \
                    series.quantile(q=self._outlierTailProportion[col],
                                    interpolation='linear')

                sampleMin: PyNumType = self.sampleStat(col, stat='min')
                sampleMedian: PyNumType = self.sampleStat(col, stat='median')

                result = (series.loc[series > sampleMin].min(axis='index', skipna=True, level=None)
                          if (outlierRstMin == sampleMin) and (outlierRstMin < sampleMedian)
                          else outlierRstMin)

                if isinstance(result, NUMPY_FLOAT_TYPES):
                    result: float = float(result)

                elif isinstance(result, NUMPY_INT_TYPES):
                    result: int = int(result)

                assert isinstance(result, PY_NUM_TYPES + (NAType,)), \
                    TypeError(f'*** "{col}" OUTLIER-RESISTANT MIN = '
                              f'{result} ({type(result)}) ***')

                if verbose:
                    toc: float = time.time()
                    self.stdOutLogger.info(msg=f'Outlier-Resistant Min of Column "{col}" = '
                                               f'{result:,.3g}   <{toc - tic:,.1f} s>')

                self._cache.outlierRstMin[col] = result

            return self._cache.outlierRstMin[col]

        raise ValueError(f'*** {self}.outlierRstMin({col}, ...): '
                         f'COLUMN "{col}" NOT NUMERICAL ***')

    def outlierRstMax(self, *cols: str, **kwargs: Any) -> Union[float, int, Namespace]:
        """Return outlier-resistant maximum for specified column(s)."""
        if not cols:
            cols: Set[str] = self.possibleNumCols

        if len(cols) > 1:
            return Namespace(**{col: self.outlierRstMax(col, **kwargs) for col in cols})

        col: str = cols[0]

        if self.typeIsNum(col):
            if 'outlierRstMax' not in self._cache:
                self._cache.outlierRstMax = {}

            if col not in self._cache.outlierRstMax:
                verbose: Optional[bool] = True if debug.ON else kwargs.get('verbose')

                if verbose:
                    tic: float = time.time()

                series: Series = self.reprSample[col]

                outlierRstMax: PyNumType = \
                    series.quantile(q=1 - self._outlierTailProportion[col],
                                    interpolation='linear')

                sampleMax: PyNumType = self.sampleStat(col, stat='max')
                sampleMedian: PyNumType = self.sampleStat(col, stat='median')

                result = (series.loc[series < sampleMax].max(axis='index', skipna=True, level=None)
                          if (outlierRstMax == sampleMax) and (outlierRstMax > sampleMedian)
                          else outlierRstMax)

                if isinstance(result, NUMPY_FLOAT_TYPES):
                    result: float = float(result)

                elif isinstance(result, NUMPY_INT_TYPES):
                    result: int = int(result)

                assert isinstance(result, PY_NUM_TYPES + (NAType,)), \
                    TypeError(f'*** "{col}" OUTLIER-RESISTANT MAX = {result} '
                              f'({type(result)}) ***')

                if verbose:
                    toc: float = time.time()
                    self.stdOutLogger.info(msg=f'Outlier-Resistant Max of Column "{col}" = '
                                               f'{result:,.3g}   <{toc - tic:,.1f} s>')

                self._cache.outlierRstMax[col] = result

            return self._cache.outlierRstMax[col]

        raise ValueError(f'*** {self}.outlierRstMax({col}, ...): '
                         f'COLUMN "{col}" NOT NUMERICAL ***')

    def profile(self, *cols: str, **kwargs: Any) -> Namespace:
        # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        """Profile specified column(s).

        Return:
            *dict* of profile of salient statistics on
            specified columns of ``ADF``

        Args:
            *cols (str): names of column(s) to profile

            **kwargs:

                - **profileCat** *(bool, default = True)*:
                whether to profile possible categorical columns

                - **profileNum** *(bool, default = True)*:
                whether to profile numerical columns

                - **skipIfInsuffNonNull** *(bool, default = False)*:
                whether to skip profiling if column does not have
                enough non-NULLs
        """
        if not cols:
            cols: Set[str] = self.contentCols

        asDict: bool = kwargs.pop('asDict', False)

        if len(cols) > 1:
            return Namespace(**{col: self.profile(col, **kwargs) for col in cols})

        col: str = cols[0]

        verbose: Optional[Union[bool, int]] = True if debug.ON else kwargs.get('verbose')

        if verbose:
            self.stdOutLogger.info(msg=(msg := f'Profiling Column "{col}"...'))
            tic: float = time.time()

        colType: DataType = self.type(col)
        profile: Namespace = Namespace(type=colType)

        # non-NULL Proportions
        profile.nonNullProportion = self.nonNullProportion(col, verbose=verbose > 1)

        if self.suffNonNull(col) or (not kwargs.get('skipIfInsuffNonNull', False)):
            # profile categorical column
            if kwargs.get('profileCat', True) and is_possible_cat(colType):
                profile.distinctProportions = self.distinct(col, verbose=verbose > 1)

            # profile numerical column
            if kwargs.get('profileNum', True) and self.typeIsNum(col):
                outlierTailProportion: float = self._outlierTailProportion[col]

                quantilesOfInterest: Series = Series(index=(0,
                                                            outlierTailProportion,
                                                            .5,
                                                            1 - outlierTailProportion,
                                                            1))
                quantileProbsToQuery: List[float] = []

                sampleMin: Optional[PyNumType] = self._cache.sampleMin.get(col)
                if calcAndCacheSampleMin := (sampleMin is None):
                    quantileProbsToQuery.append(0.)
                else:
                    quantilesOfInterest[0] = sampleMin

                outlierRstMin: Optional[PyNumType] = self._cache.outlierRstMin.get(col)
                if calcAndCacheOutlierRstMin := (outlierRstMin is None):
                    quantileProbsToQuery.append(outlierTailProportion)
                else:
                    quantilesOfInterest[outlierTailProportion] = outlierRstMin

                sampleMedian: Optional[PyNumType] = self._cache.sampleMedian.get(col)
                if calcAndCacheSampleMedian := (sampleMedian is None):
                    quantileProbsToQuery.append(.5)
                else:
                    quantilesOfInterest[.5] = sampleMedian

                outlierRstMax: Optional[PyNumType] = self._cache.outlierRstMax.get(col)
                if calcAndCacheOutlierRstMax := (outlierRstMax is None):
                    quantileProbsToQuery.append(1 - outlierTailProportion)
                else:
                    quantilesOfInterest[1 - outlierTailProportion] = outlierRstMax

                sampleMax: Optional[PyNumType] = self._cache.sampleMax.get(col)
                if calcAndCacheSampleMax := (sampleMax is None):
                    quantileProbsToQuery.append(1.)
                else:
                    quantilesOfInterest[1] = sampleMax

                series: Series = self.reprSample[col]

                if quantileProbsToQuery:
                    quantilesOfInterest.mask(
                        cond=quantilesOfInterest.isnull(),
                        other=series.quantile(q=quantileProbsToQuery, interpolation='linear'),
                        inplace=True,
                        axis=None,
                        level=None)

                (sampleMin, outlierRstMin,
                 sampleMedian,
                 outlierRstMax, sampleMax) = quantilesOfInterest

                if calcAndCacheSampleMin:
                    self._cache.sampleMin[col] = sampleMin

                if calcAndCacheOutlierRstMin:
                    if (outlierRstMin == sampleMin) and (outlierRstMin < sampleMedian):
                        outlierRstMin: PyNumType = (
                            series.loc[series > sampleMin]
                            .min(axis='index', skipna=True, level=None))

                    self._cache.outlierRstMin[col] = outlierRstMin

                if calcAndCacheSampleMedian:
                    self._cache.sampleMedian[col] = sampleMedian

                if calcAndCacheOutlierRstMax:
                    if (outlierRstMax == sampleMax) and (outlierRstMax > sampleMedian):
                        outlierRstMax: PyNumType = (
                            series.loc[series < sampleMax]
                            .max(axis='index', skipna=True, level=None))

                    self._cache.outlierRstMax[col] = outlierRstMax

                if calcAndCacheSampleMax:
                    self._cache.sampleMax[col] = sampleMax

                profile.sampleRange = sampleMin, sampleMax
                profile.outlierRstRange = outlierRstMin, outlierRstMax

                profile.sampleMean = self.sampleStat(col, stat='mean', verbose=verbose)

                profile.outlierRstMean = \
                    self._cache.outlierRstMean.get(
                        col,
                        self.outlierRstStat(col, stat='mean', verbose=verbose))

                profile.outlierRstMedian = \
                    self._cache.outlierRstMedian.get(
                        col,
                        self.outlierRstStat(col, stat='median', verbose=verbose))

        if verbose:
            toc: float = time.time()
            self.stdOutLogger.info(msg=f'{msg} done!   <{toc - tic:,.1f} s>')

        return Namespace(**{col: profile}) if asDict else profile

    # ====================
    # PREPROCESSING FOR ML
    # --------------------
    # preprocForML

    def preprocForML(self, *cols: str, **kwargs: Any) -> ParquetDataset:
        # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        """Preprocess column(s) for ML training/inferencing.

        Return:
            Preprocessed (incl. numerical-``NULL``-filled) ``ParquetDataset``

        Args:
            *cols: column(s) to preprocess

            **kwargs:
                - **forceCat** / **forceCatIncl** / **forceCatExcl**
                *(str or list/set/tuple of str, default = None)*:
                column(s) to force/include/exclude as categorical variable(s)

                - **catIdxScaled**: whether to scale categorical indices *(bool, default = True)*

                - **forceNum** / **forceNumIncl** / **forceNumExcl**
                *(str or list/set/tuple of str, default = None)*:
                column(s) to force/include/exclude as numerical variable(s)

                - **numNulls**: *(dict of column names mapping to (numerical, numerical) tuples,
                default = None)*: pairs of lower & upper numerical nulls of certain columns

                - **numOutlierTail**: *(str or dict of column names mapping str,
                default = 'both')*: string indicating outlier tails of certain columns.
                One of:
                    - 'both'
                    - 'lower'
                    - 'upper'
                    - None

                - **numNullFill**:
                    - *dict* ( ``method`` = ... *(default: 'mean')*,
                               ``value`` = ... *(default: None)*,
                               ``outlierTail`` = ... *(default: False)* )
                    - *OR* ``None`` to not apply any ``NULL``/``NaN``-filling

                - **numScaler** *(str)*: one of the following methods to use on numerical columns
                (*ignored* if loading existing ``prep`` pipeline from ``loadPath``):
                    - ``standard`` (default)
                    - ``maxabs``
                    - ``minmax``
                    - ``None`` *(do not apply any scaling)*

                - **loadPath** *(str)*: path to load existing data transformations

                - **savePath** *(str)*: path to save new fitted data transformations

                - **method** *(str)*: one of the following methods to fill
                    ``NULL`` values in **numerical** columns,
                    or *dict* of such method specifications by column name

                    - ``avg``/``mean`` (default)
                    - ``min``
                    - ``max``
                    - ``None`` (do nothing)

                - **value**: single value, or *dict* of values by column name,
                    to use if ``method`` is ``None`` or not applicable

                - **outlierTail** *(str or dict of str, default = 'both')*:
                specification of in which distribution tail
                (``None``, ``lower``, ``upper`` and ``both`` (default))
                of each numerical column out-lying values may exist
        """
        returnNumPy: bool = kwargs.pop('returnNumPy', False)

        returnPreproc: bool = kwargs.pop('returnPreproc', False)

        verbose: Union[bool, int] = kwargs.pop('verbose', True)
        if debug.ON:
            verbose: bool = True

        if loadPath := kwargs.pop('loadPath', None):   # pylint: disable=too-many-nested-blocks
            if verbose:
                self.stdOutLogger.info(msg=(msg := ('Loading & Applying Data Transformations '
                                                    f'from "{loadPath}"...')))
                tic: float = time.time()

            pandasMLPreproc: PandasMLPreprocessor = PandasMLPreprocessor.from_yaml(path=loadPath)

        else:
            cols: Set[str] = {col
                              for col in ((set(cols) & self.possibleFeatureCols)
                                          if cols
                                          else self.possibleFeatureCols)
                              if self.suffNonNull(col)}

            assert cols, ValueError(f'*** {self}: NO COLS WITH SUFFICIENT NON-NULLS ***')

            profile: Namespace = self.profile(*cols,
                                              profileCat=True, profileNum=False,
                                              skipIfInsuffNonNull=True,
                                              asDict=True, verbose=verbose)

            cols: Set[str] = {col
                              for col in cols
                              if ((distinctProportionsIndex :=
                                   profile[col].distinctProportions.index).notnull() &
                                  (distinctProportionsIndex != '')).sum() > 1}

            assert cols, ValueError(f'*** {self}: NO COLS WITH SUFFICIENT DISTINCT VALUES ***')

            forceCat: Set[str] = (((to_iterable(forceCat, iterable_type=set)
                                    if (forceCat := kwargs.pop('forceCat', None))
                                    else set())
                                   | (to_iterable(forceCatIncl, iterable_type=set)
                                      if (forceCatIncl := kwargs.pop('forceCatIncl', None))
                                      else set()))
                                  - (to_iterable(forceCatExcl, iterable_type=set)
                                     if (forceCatExcl := kwargs.pop('forceCatExcl', None))
                                     else set()))

            forceNum: Set[str] = (((to_iterable(forceNum, iterable_type=set)
                                    if (forceNum := kwargs.pop('forceNum', None))
                                    else set())
                                   | (to_iterable(forceNumIncl, iterable_type=set)
                                      if (forceNumIncl := kwargs.pop('forceNumIncl', None))
                                      else set()))
                                  - (to_iterable(forceNumExcl, iterable_type=set)
                                     if (forceNumExcl := kwargs.pop('forceNumExcl', None))
                                     else set()))

            catCols: Set[str] = {col
                                 for col in ((cols & self.possibleCatCols) - forceNum)
                                 if (col in forceCat) or
                                    (profile[col].distinctProportions
                                     .iloc[:self._maxNCats[col]].sum()
                                     >= self._minProportionByMaxNCats[col])}

            numCols: Set[str] = {col for col in (cols - catCols) if self.typeIsNum(col)}

            cols: Set[str] = catCols | numCols

            if verbose:
                self.stdOutLogger.info(msg=(msg := ('Preprocessing Columns ' +
                                                    ', '.join(f'"{col}"' for col in cols) +
                                                    '...')))
                tic: float = time.time()

            origToPreprocColMap: Namespace = Namespace()

            if catCols:
                if verbose:
                    self.stdOutLogger.info(
                        msg=(cat_prep_msg := ('Transforming Categorical Columns ' +
                                              ', '.join(f'"{catCol}"' for catCol in catCols) +
                                              '...')))
                    cat_prep_tic: float = time.time()

                origToPreprocColMap[PandasMLPreprocessor._CAT_INDEX_SCALED_FIELD_NAME] = \
                    (catIdxScaled := kwargs.pop('catIdxScaled', True))

                catIdxCols: Set[str] = set()

                if catIdxScaled:
                    catScaledIdxCols: Set[str] = set()

                for catCol in catCols:
                    catIdxCol: str = self._CAT_IDX_PREFIX + catCol

                    catColType: DataType = self.type(catCol)

                    if is_boolean(catColType):
                        sortedCats: Tuple[bool] = False, True
                        nCats: int = 2

                    else:
                        isStr: bool = is_string(catColType)

                        sortedCats: Tuple[PyPossibleFeatureType] = tuple(
                            cat
                            for cat in
                            (profile[catCol].distinctProportions.index
                             if catCol in forceCat
                             else (profile[catCol].distinctProportions
                                   .index[:self._maxNCats[catCol]]))
                            if notnull(cat) and
                            ((cat != '') if isStr else isfinite(cat)))

                        nCats: int = len(sortedCats)

                    if catIdxScaled:
                        catPrepCol: str = self._MIN_MAX_SCL_PREFIX + catIdxCol
                        catScaledIdxCols.add(catPrepCol)

                    else:
                        catPrepCol: str = catIdxCol
                        catIdxCols.add(catPrepCol)

                    origToPreprocColMap[catCol] = {'logical-type': 'cat',
                                                   'physical-type': str(catColType),
                                                   'n-cats': nCats, 'sorted-cats': sortedCats,
                                                   'transform-to': catPrepCol}

                if verbose:
                    cat_prep_toc: float = time.time()
                    self.stdOutLogger.info(
                        msg=f'{cat_prep_msg} done!   <{cat_prep_toc - cat_prep_tic:,.1f} s>')

            if numCols:
                origToPreprocColMap[PandasMLPreprocessor._NUM_SCALER_FIELD_NAME] = \
                    (numScaler := kwargs.pop('numScaler', 'standard'))

                numNulls: Dict[str, Tuple[Optional[PyNumType], Optional[PyNumType]]] = \
                    kwargs.pop('numNulls', {})

                numOutlierTail: Optional[Union[str, Dict[str, Optional[str]]]] = \
                    kwargs.pop('numOutlierTail', 'both')
                if not isinstance(numOutlierTail, DICT_OR_NAMESPACE_TYPES):
                    numOutlierTail: Dict[str, Optional[str]] = \
                        {col: numOutlierTail for col in numCols}

                numNullFillMethod: Union[str, Dict[str, str]] = \
                    kwargs.pop('numNullFillMethod', 'mean')
                if not isinstance(numNullFillMethod, DICT_OR_NAMESPACE_TYPES):
                    numNullFillMethod: Dict[str, str] = \
                        {col: numNullFillMethod for col in numCols}

                numNullFillValue: Dict[str, Optional[PyNumType]] = \
                    kwargs.pop('numNullFillValue', {})

                numScaledCols: Set[str] = set()

                if verbose:
                    self.stdOutLogger.info(
                        msg=(num_prep_msg := (
                            'Transforming (incl. NULL-Filling) Numerical Columns ' +
                            ', '.join(f'"{numCol}"' for numCol in numCols) + '...')))
                    num_prep_tic: float = time.time()

                for numCol in numCols:
                    if numCol in numNulls:
                        numColNulls: Tuple[Optional[PyNumType], Optional[PyNumType]] = \
                            numNulls[numCol]

                        assert (isinstance(numColNulls, PY_LIST_OR_TUPLE) and
                                (len(numColNulls) == 2) and
                                ((numColNulls[0] is None) or
                                 isinstance(numColNulls[0], PY_NUM_TYPES)) and
                                ((numColNulls[1] is None) or
                                 isinstance(numColNulls[1], PY_NUM_TYPES)))

                    else:
                        numColNulls: Tuple[Optional[PyNumType], Optional[PyNumType]] = None, None

                    numColOutlierTail: Optional[str] = numOutlierTail.get(numCol, 'both')

                    numColMin: PyNumType = (self.outlierRstMin(numCol)
                                            if numColOutlierTail in ('lower', 'both')
                                            else self.sampleStat(numCol, stat='min'))

                    numColMax: PyNumType = (self.outlierRstMax(numCol)
                                            if numColOutlierTail in ('upper', 'both')
                                            else self.sampleStat(numCol, stat='max'))

                    if numColMin < numColMax:
                        numColType: DataType = self.type(numCol)

                        if numColNullFillMethod := numNullFillMethod.get(numCol, 'mean'):
                            numColNullFillValue: PyNumType = \
                                self.outlierRstStat(numCol,
                                                    stat=numColNullFillMethod,
                                                    outlierTail=numColOutlierTail,
                                                    verbose=verbose > 1)

                        else:
                            numColNullFillValue: Optional[PyNumType] = numNullFillValue.get(numCol)

                            if not isinstance(numColNullFillValue, PY_NUM_TYPES):
                                numColNullFillValue: Optional[PyNumType] = None

                        if numScaler:
                            if numScaler == 'standard':
                                scaledCol: str = self._STD_SCL_PREFIX + numCol

                                series: Series = self.reprSample[numCol]

                                if numColOutlierTail == 'both':
                                    series: Series = series.loc[series.between(left=numColMin,
                                                                               right=numColMax,
                                                                               inclusive='both')]

                                elif numColOutlierTail == 'lower':
                                    series: Series = series.loc[series > numColMin]

                                elif numColOutlierTail == 'upper':
                                    series: Series = series.loc[series < numColMax]

                                stdDev: float = float(series.std(axis='index',
                                                                 skipna=True,
                                                                 level=None,
                                                                 ddof=1))

                                origToPreprocColMap[numCol] = {
                                    'logical-type': 'num',
                                    'physical-type': str(numColType),
                                    'nulls': numColNulls,
                                    'null-fill-method': numColNullFillMethod,
                                    'null-fill-value': numColNullFillValue,
                                    'mean': numColNullFillValue, 'std': stdDev,
                                    'transform-to': scaledCol}

                            elif numScaler == 'maxabs':
                                scaledCol: str = self._MAX_ABS_SCL_PREFIX + numCol

                                maxAbs: PyNumType = max(abs(numColMin), abs(numColMax))

                                origToPreprocColMap[numCol] = {
                                    'logical-type': 'num',
                                    'physical-type': str(numColType),
                                    'nulls': numColNulls,
                                    'null-fill-method': numColNullFillMethod,
                                    'null-fill-value': numColNullFillValue,
                                    'max-abs': maxAbs,
                                    'transform-to': scaledCol}

                            elif numScaler == 'minmax':
                                scaledCol: str = self._MIN_MAX_SCL_PREFIX + numCol

                                origToPreprocColMap[numCol] = {
                                    'logical-type': 'num',
                                    'physical-type': str(numColType),
                                    'nulls': numColNulls,
                                    'null-fill-method': numColNullFillMethod,
                                    'null-fill-value': numColNullFillValue,
                                    'orig-min': numColMin, 'orig-max': numColMax,
                                    'target-min': -1, 'target-max': 1,
                                    'transform-to': scaledCol}

                            else:
                                raise ValueError('*** Scaler must be one of '
                                                 '"standard", "maxabs", "minmax" '
                                                 'and None ***')

                        else:
                            scaledCol: str = self._NULL_FILL_PREFIX + numCol

                            origToPreprocColMap[numCol] = {
                                'logical-type': 'num',
                                'physical-type': str(numColType),
                                'nulls': numColNulls,
                                'null-fill-method': numColNullFillMethod,
                                'null-fill-value': numColNullFillValue,
                                'transform-to': scaledCol}

                        numScaledCols.add(scaledCol)

                if verbose:
                    num_prep_toc: float = time.time()
                    self.stdOutLogger.info(
                        msg=f'{num_prep_msg} done!   <{num_prep_toc - num_prep_tic:,.1f} s>')

            pandasMLPreproc: PandasMLPreprocessor = \
                PandasMLPreprocessor(origToPreprocColMap=origToPreprocColMap)

            if savePath := kwargs.pop('savePath', None):
                if verbose:
                    self.stdOutLogger.info(
                        msg=(prep_save_msg := ('Saving Data Transformations '
                                               f'to Local Path "{savePath}"...')))
                    prep_save_tic: float = time.time()

                pandasMLPreproc.to_yaml(path=savePath)

                if verbose:
                    prep_save_toc: float = time.time()
                    self.stdOutLogger.info(
                        msg=f'{prep_save_msg} done!   <{prep_save_toc - prep_save_tic:,.1f} s>')

        if returnNumPy:
            s3ParquetDF: ParquetDataset = \
                self.map(partial(pandasMLPreproc.__call__, returnNumPy=True),
                         inheritNRows=True, **kwargs)

        else:
            colsToKeep: Set[str] = self.indexCols | (
                set(chain.from_iterable(
                    (catCol, catPrepColDetails['transform-to'])
                    for catCol, catPrepColDetails in origToPreprocColMap.items()
                    if (catCol not in (PandasMLPreprocessor._CAT_INDEX_SCALED_FIELD_NAME,
                                       PandasMLPreprocessor._NUM_SCALER_FIELD_NAME))
                    and (catPrepColDetails['logical-type'] == 'cat')))
                |
                set(chain.from_iterable(
                    (numCol, numPrepColDetails['transform-to'])
                    for numCol, numPrepColDetails in origToPreprocColMap.items()
                    if (numCol not in (PandasMLPreprocessor._CAT_INDEX_SCALED_FIELD_NAME,
                                       PandasMLPreprocessor._NUM_SCALER_FIELD_NAME))
                    and (numPrepColDetails['logical-type'] == 'num'))))

            s3ParquetDF: ParquetDataset = \
                self.map(pandasMLPreproc, inheritNRows=True, **kwargs)[tuple(colsToKeep)]
            s3ParquetDF._inheritCache(self, *colsToKeep)
            s3ParquetDF._cache.reprSample = self._cache.reprSample

        if verbose:
            toc: float = time.time()
            self.stdOutLogger.info(msg=f'{msg} done!   <{(toc - tic) / 60:,.1f} m>')

        return (s3ParquetDF, pandasMLPreproc) if returnPreproc else s3ParquetDF
