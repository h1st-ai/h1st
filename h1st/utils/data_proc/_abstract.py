"""Abstract Data Handlers."""


from __future__ import annotations

from logging import getLogger, Logger, Handler, DEBUG, INFO
from pathlib import Path
import tempfile
from typing import Any, Optional, Union
from typing import Collection, Dict, Set, Tuple   # Py3.9+: built-ins

from numpy import ndarray
from pandas import DataFrame, Series

from h1st.utils import debug
from h1st.utils.log import STDOUT_HANDLER
from h1st.utils.namespace import Namespace


__all__ = (
    'AbstractDataHandler', 'AbstractFileDataHandler', 'AbstractS3FileDataHandler',   # noqa: E501
    'ColsType', 'ReducedDataSetType',
)


ColsType = Union[str, Collection[str]]
ReducedDataSetType = Union[Any, Collection, ndarray, DataFrame, Series]


class AbstractDataHandler:
    # pylint: disable=no-member,too-many-public-methods
    """Abstract Data Handler."""

    # ===========
    # CLASS ATTRS
    # -----------

    # date column name
    _DATE_COL: str = 'date'

    # default representative sample size
    _DEFAULT_REPR_SAMPLE_SIZE: int = 10 ** 6

    # default column profiling settings
    _DEFAULT_MIN_NON_NULL_PROPORTION: float = .32
    _DEFAULT_OUTLIER_TAIL_PROPORTION: float = 1e-3   # 0.1% each tail
    _DEFAULT_MAX_N_CATS: int = 12   # MoY is likely most numerous-category var
    _DEFAULT_MIN_PROPORTION_BY_MAX_N_CATS: float = .9

    # preprocessing for ML
    _CAT_IDX_PREFIX: str = 'CAT_INDEX__'

    _NULL_FILL_PREFIX: str = 'NULL_FILLED__'

    _STD_SCL_PREFIX: str = 'STD_SCALED__'
    _MAX_ABS_SCL_PREFIX: str = 'MAXABS_SCALED__'
    _MIN_MAX_SCL_PREFIX: str = 'MINMAX_SCALED__'

    # ===========
    # STRING REPR
    # -----------
    # __repr__
    # __shortRepr__
    # __str__

    def __repr__(self) -> str:
        """Return string repr."""
        raise NotImplementedError

    @property
    def __shortRepr__(self) -> str:   # noqa: N802
        # pylint: disable=invalid-name
        """Return short string repr."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Return string repr."""
        return repr(self)

    # =======
    # LOGGING
    # -------
    # classLogger
    # classStdOutLogger
    # logger
    # stdOutLogger

    @classmethod
    def classLogger(cls, *handlers: Handler, **kwargs: Any) -> Logger:   # noqa: E501,N802
        # pylint: disable=invalid-name
        """Get Class Logger."""
        logger: Logger = getLogger(name=cls.__name__)

        level: Optional[int] = kwargs.get('level')
        if not level:
            level: int = DEBUG if debug.ON else INFO
        logger.setLevel(level=level)

        for handler in handlers:
            logger.addHandler(hdlr=handler)
        if kwargs.get('verbose'):
            logger.addHandler(hdlr=STDOUT_HANDLER)

        return logger

    @classmethod
    def classStdOutLogger(cls) -> Logger:   # noqa: N802
        # pylint: disable=invalid-name
        """Get Class StdOut Logger."""
        return cls.classLogger(level=DEBUG, verbose=True)

    def logger(self, *handlers: Handler, **kwargs: Any) -> Logger:
        """Get Logger."""
        logger: Logger = getLogger(name=self.__shortRepr__)

        level: Optional[int] = kwargs.get('level')
        if not level:
            level: int = DEBUG if debug.ON else INFO
        logger.setLevel(level=level)

        for handler in handlers:
            logger.addHandler(hdlr=handler)
        if kwargs.get('verbose'):
            logger.addHandler(hdlr=STDOUT_HANDLER)

        return logger

    @property
    def stdOutLogger(self) -> Logger:   # noqa: N802
        # pylint: disable=invalid-name
        """Get StdOut Logger."""
        return self.logger(level=DEBUG, verbose=True)

    # ===================
    # SETTABLE PROPERTIES
    # -------------------
    # iCol
    # tCol

    @property
    def iCol(self) -> Optional[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Entity/Identity column."""
        return self._iCol

    @iCol.setter
    def iCol(self, iCol: str):   # noqa: N802,N803
        # pylint: disable=invalid-name
        if iCol != self._iCol:
            self._iCol: Optional[str] = iCol

            if iCol is not None:
                assert iCol, ValueError(f'*** iCol {iCol} INVALID ***')

    @iCol.deleter
    def iCol(self):   # noqa: N802
        # pylint: disable=invalid-name
        self._iCol: Optional[str] = None

    @property
    def tCol(self) -> Optional[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Date-Time column."""
        return self._tCol

    @tCol.setter
    def tCol(self, tCol: str):   # noqa: N802,N803
        # pylint: disable=invalid-name
        if tCol != self._tCol:
            self._tCol: Optional[str] = tCol

            if tCol is not None:
                assert tCol, ValueError(f'*** tCol {tCol} INVALID ***')

    @tCol.deleter
    def tCol(self):   # noqa: N802
        # pylint: disable=invalid-name
        self._tCol: Optional[str] = None

    # =======
    # CACHING
    # -------
    # _emptyCache
    # _inheritCache

    def _emptyCache(self):   # noqa: N802
        # pylint: disable=invalid-name
        """Empty cache."""
        raise NotImplementedError

    def _inheritCache(self, *args: Any, **kwargs: Any):   # noqa: N802
        # pylint: disable=invalid-name
        """Inherit existing cache."""
        raise NotImplementedError

    # =====================
    # ROWS, COLUMNS & TYPES
    # ---------------------
    # __len__ / nRows
    # columns
    # _organizeIndexCols
    # indexCols
    # contentCols
    # types / type / typeIsNum
    # possibleFeatureCols
    # possibleCatCols
    # possibleNumCols

    def __len__(self) -> int:
        """Return number of rows."""
        return self.nRows

    @property
    def nRows(self) -> int:   # noqa: N802
        # pylint: disable=invalid-name
        """Return number of rows."""
        raise NotImplementedError

    @nRows.deleter
    def nRows(self):   # noqa: N802
        # pylint: disable=invalid-name
        self._cache.nRows = None

    @property
    def columns(self) -> Set[str]:
        """Return columns."""
        raise NotImplementedError

    def _organizeIndexCols(self):   # noqa: N802
        # pylint: disable=attribute-defined-outside-init,invalid-name
        self._dCol: Optional[str] = (self._DATE_COL
                                     if self._DATE_COL in self.columns
                                     else None)

    @property
    def indexCols(self) -> Set[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Return index columns."""
        raise NotImplementedError

    @property
    def contentCols(self) -> Set[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Return content columns."""
        return self.columns - self.indexCols

    @property
    def types(self) -> Namespace:
        """Return column data types."""
        raise NotImplementedError

    def type(self, col: str) -> type:
        """Return data type of specified column."""
        raise NotImplementedError

    def typeIsNum(self, col: str) -> bool:   # noqa: N802
        # pylint: disable=invalid-name
        """Check whether specified column's data type is numerical."""
        raise NotImplementedError

    @property
    def possibleFeatureCols(self) -> Set[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Return possible feature content columns."""
        raise NotImplementedError

    @property
    def possibleCatCols(self) -> Set[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Return possible categorical content columns."""
        raise NotImplementedError

    @property
    def possibleNumCols(self) -> Set[str]:   # noqa: N802
        # pylint: disable=invalid-name
        """Return possible numerical content columns."""
        return {col for col in self.contentCols if self.typeIsNum(col)}

    # =========
    # FILTERING
    # ---------
    # filter

    def filter(self, *conditions: str, **kwargs: Any) -> AbstractDataHandler:
        """Apply filtering conditions."""
        raise NotImplementedError

    # ========
    # SAMPLING
    # --------
    # sample
    # _assignReprSample
    # reprSampleSize
    # reprSample

    def sample(self, *cols: str, **kwargs: Any) -> Union[ReducedDataSetType, Any]:   # noqa: E501
        """Sample from data set."""
        raise NotImplementedError

    def _assignReprSample(self):   # noqa: N802
        # pylint: disable=invalid-name
        """Assign representative sample."""
        raise NotImplementedError

    @property
    def reprSampleSize(self) -> int:   # noqa: N802
        # pylint: disable=invalid-name
        """Return approx number of rows to sample for profiling purposes.

        (default = 1,000,000)
        """
        if self._cache.reprSample is None:
            self._assignReprSample()

        return self._reprSampleSize

    @reprSampleSize.setter
    def reprSampleSize(self, n: int, /):   # noqa: N802
        # pylint: disable=invalid-name
        self._reprSampleSize: int = n
        self._assignReprSample()

    @property
    def reprSample(self):   # noqa: N802
        # pylint: disable=invalid-name
        """Sub-sampled data set according to ``.reprSampleSize`` attribute."""
        if self._cache.reprSample is None:
            self._assignReprSample()

        return self._cache.reprSample

    # ================
    # COLUMN PROFILING
    # ----------------
    # minNonNullProportion
    # outlierTailProportion
    # maxNCats
    # minProportionByMaxNCats
    # count
    # nonNullProportion
    # suffNonNull
    # distinct
    # quantile
    # sampleStat
    # outlierRstStat
    # profile

    @property
    def minNonNullProportion(self) -> float:   # noqa: N802
        # pylint: disable=invalid-name
        """Return min proportion of non-NULL values in each column.

        (to qualify it as a valid feature to use in downstream modeling)
        (default = .32)
        """
        return self._minNonNullProportion.default

    @minNonNullProportion.setter
    def minNonNullProportion(self, proportion: float, /):   # noqa: N802
        # pylint: disable=invalid-name
        if proportion != self._minNonNullProportion.default:
            self._minNonNullProportion.default = proportion
            self._cache.suffNonNull = {}

    @property
    def outlierTailProportion(self) -> float:   # noqa: N802
        # pylint: disable=invalid-name
        """Return proportion in each tail of each numerical column's distrib.

        (to exclude when computing outlier-resistant statistics)
        (default = .001)
        """
        return self._outlierTailProportion.default

    @outlierTailProportion.setter
    def outlierTailProportion(self, proportion: float, /):   # noqa: N802
        # pylint: disable=invalid-name
        self._outlierTailProportion.default = proportion

    @property
    def maxNCats(self) -> int:   # noqa: N802
        # pylint: disable=invalid-name
        """Return max number of categorical levels for possible cat. columns.

        (default = 12)
        """
        return self._maxNCats.default

    @maxNCats.setter
    def maxNCats(self, n: int, /):   # noqa: N802
        # pylint: disable=invalid-name
        self._maxNCats.default = n

    @property
    def minProportionByMaxNCats(self) -> float:   # noqa: N802
        # pylint: disable=invalid-name
        """Return min total proportion accounted for by top ``maxNCats``.

        (to consider the column truly categorical)
        (default = .9)
        """
        return self._minProportionByMaxNCats.default

    @minProportionByMaxNCats.setter
    def minProportionByMaxNCats(self, proportion: float, /):   # noqa: N802
        # pylint: disable=invalid-name
        self._minProportionByMaxNCats.default = proportion

    def count(self, *cols: str, **kwargs: Any) -> Union[int, Namespace]:
        """Count non-NULL data values in specified column(s)."""
        raise NotImplementedError

    def nonNullProportion(self, *cols: str, **kwargs: Any) \
            -> Union[float, Namespace]:   # noqa: N802
        # pylint: disable=invalid-name
        """Count non-NULL data proportion(s) in specified column(s)."""
        raise NotImplementedError

    def suffNonNull(self, *cols: str, **kwargs: Any) -> Union[bool, Namespace]:   # noqa: E501,N802
        # pylint: disable=invalid-name:
        """Check whether columns have sufficient non-NULL values.

        (at least ``.minNonNullProportion`` of values being non-``NULL``)

        Return:
            - If 1 column name is given, return ``True``/``False``

            - If multiple column names are given,
            return a {``col``: ``True`` or ``False``} *dict*

            - If no column names are given,
            return a {``col``: ``True`` or ``False``} *dict* for all columns
        """
        if not cols:
            cols: Tuple[str] = tuple(self.contentCols)

        if len(cols) > 1:
            return Namespace(**{col: self.suffNonNull(col, **kwargs)
                                for col in cols})

        col: str = cols[0]

        minNonNullProportion: float = self._minNonNullProportion[col]   # noqa: E501,N806

        outdatedSuffNonNullProportionThreshold: bool = False   # noqa: N806

        if col in self._cache.suffNonNullProportionThreshold:
            if self._cache.suffNonNullProportionThreshold[col] != \
                    minNonNullProportion:
                outdatedSuffNonNullProportionThreshold: bool = True   # noqa: E501,N806
                self._cache.suffNonNullProportionThreshold[col] = \
                    minNonNullProportion

        else:
            self._cache.suffNonNullProportionThreshold[col] = \
                minNonNullProportion

        if (col not in self._cache.suffNonNull) or \
                outdatedSuffNonNullProportionThreshold:
            self._cache.suffNonNull[col] = (
                self.nonNullProportion(col) >=
                self._cache.suffNonNullProportionThreshold[col])

        return self._cache.suffNonNull[col]

    def distinct(self, *cols: str, **kwargs: Any) -> Union[Dict[str, float],
                                                           Series, Namespace]:
        """Return distinct values for specified column(s)."""
        raise NotImplementedError

    def quantile(self, *cols: str, **kwargs: Any) -> Union[float, int,
                                                           Series, Namespace]:
        """Return quantile values for specified column(s)."""
        raise NotImplementedError

    def sampleStat(self, *cols: str, **kwargs: Any) \
            -> Union[float, int, Namespace]:   # noqa: N802
        # pylint: disable=invalid-name:
        """Return certain sample statistics for specified columns."""
        raise NotImplementedError

    def outlierRstStat(self, *cols: str, **kwargs: Any) \
            -> Union[float, int, Namespace]:   # noqa: N802
        # pylint: disable=invalid-name:
        """Return outlier-resistant statistics for specified columns."""
        raise NotImplementedError

    def profile(self, *cols: str, **kwargs: Any) -> Namespace:
        """Profile specified column(s)."""
        raise NotImplementedError

    # ====================
    # PREPROCESSING FOR ML
    # --------------------
    # preprocForML

    def preprocForML(self, *cols: str, **kwargs: Any) -> AbstractDataHandler:   # noqa: E501,N802
        # pylint: disable=invalid-name
        """Pre-process specified column(s) for ML model training/inference."""
        raise NotImplementedError


class AbstractFileDataHandler(AbstractDataHandler):
    # pylint: disable=abstract-method
    """Abstract File Data Handler."""

    # minimum number of files for schema management & representative sampling
    _SCHEMA_MIN_N_FILES: int = 10
    _REPR_SAMPLE_MIN_N_FILES: int = 100

    # local file cache dir
    _LOCAL_CACHE_DIR_PATH: Path = (Path(tempfile.gettempdir()).resolve(strict=True) /   # noqa: E501
                                   '.h1st/data-proc-cache')

    # ====================================
    # MIN. NO. OF FILES FOR REPR. SAMPLING
    # ------------------------------------
    # reprSampleMinNFiles

    @property
    def reprSampleMinNFiles(self) -> int:   # noqa: N802
        # pylint: disable=invalid-name
        """Minimum number of pieces for reprensetative sample."""
        return self._reprSampleMinNFiles

    @reprSampleMinNFiles.setter
    def reprSampleMinNFiles(self, n: int, /):   # noqa: N802
        # pylint: disable=invalid-name,no-member
        if (n <= self.nFiles) and (n != self._reprSampleMinNFiles):
            self._reprSampleMinNFiles: int = n

    @reprSampleMinNFiles.deleter
    def reprSampleMinNFiles(self):   # noqa: N802
        # pylint: disable=invalid-name,no-member
        self._reprSampleMinNFiles: int = min(self._REPR_SAMPLE_MIN_N_FILES,
                                             self.nFiles)


class AbstractS3FileDataHandler(AbstractFileDataHandler):
    # pylint: disable=abstract-method
    """Abstract S3 File Data Handler."""

    # temporary dir key
    _TMP_DIR_S3_KEY: str = 'tmp'
