"""Equipment data stored in Parquet files on S3.

(organized by Equipment Unique Type Group by Date)
"""

from dataclasses import dataclass
from functools import cached_property, lru_cache
import os
from typing import Literal, Optional
from typing import List   # Py3.9+: use built-ins

from dotenv.main import load_dotenv
from pandas import DataFrame

from h1st.utils.data_proc import ParquetDataset


load_dotenv(dotenv_path='.env',
            stream=None,
            verbose=True,
            override=False,
            interpolate=True,
            encoding='utf-8')


AWS_REGION: Optional[str] = os.environ.get('H1ST_PMFP_AWS_REGION')
AWS_ACCESS_KEY: Optional[str] = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY: Optional[str] = os.environ.get('AWS_SECRET_ACCESS_KEY')
EQUIPMENT_DATA_PARENT_DIR_PATH: Optional[str] = \
    os.environ.get('H1ST_PMFP_EQUIPMENT_DATA_PARENT_DIR_PATH')
EQUIPMENT_DATA_TIMEZONE: Optional[str] = \
    os.environ.get('H1ST_PMFP_EQUIPMENT_DATA_TIMEZONE')


EQUIPMENT_INSTANCE_ID_COL: str = 'equipment_instance_id'
DATE_COL: str = 'date'
DATE_TIME_COL: str = 'date_time'


@dataclass(init=True,
           repr=True,
           eq=True,
           order=True,
           unsafe_hash=False,
           frozen=True)   # frozen=True needed for __hash__()
class EquipmentParquetDataSet:
    """Equipment Unique Type Group Parquet Data Set."""

    general_type: Literal['refrig', 'disp_case']
    unique_type_group: str

    @cached_property
    def name(self) -> str:
        """Name data set."""
        return f'{self.general_type.upper()}---{self.unique_type_group}'

    @cached_property
    def url(self) -> str:
        """Get URL of data set."""
        assert EQUIPMENT_DATA_PARENT_DIR_PATH, \
            EnvironmentError(
                '*** H1ST_PMFP_EQUIPMENT_DATA_PARENT_DIR_PATH env var not set ***')  # noqa: E501

        return f'{EQUIPMENT_DATA_PARENT_DIR_PATH}/{self.name}.parquet'

    def __repr__(self) -> str:
        """Return string representation."""
        return f'{self.unique_type_group.upper()} data @ {self.url}'

    @lru_cache(maxsize=None, typed=False)
    def load(self) -> ParquetDataset:
        """Load as a Parquet Data Feeder."""
        if EQUIPMENT_DATA_PARENT_DIR_PATH.startswith('s3://'):
            assert AWS_REGION, \
                EnvironmentError('*** H1ST_PMFP_AWS_REGION envvar not set ***')

        return ParquetDataset(
            path=self.url,
            awsRegion=AWS_REGION,   # default is location-dependent
            accessKey=AWS_ACCESS_KEY, secretKey=AWS_SECRET_KEY,
            iCol=EQUIPMENT_INSTANCE_ID_COL, tCol=DATE_TIME_COL
        ).castType(**{EQUIPMENT_INSTANCE_ID_COL: str})

    @lru_cache(maxsize=None, typed=False)
    def get_equipment_instance_ids_by_date(
            self,
            date: Optional[str] = None, to_date: Optional[str] = None) \
            -> List[str]:
        """Get equipment instance IDs by date(s)."""
        parquet_ds: ParquetDataset = self.load()

        if date:
            try:
                parquet_ds: ParquetDataset = \
                    parquet_ds.filterByPartitionKeys((DATE_COL, date, to_date)
                                                     if to_date
                                                     else (DATE_COL, date))

            except Exception as err:   # pylint: disable=broad-except
                print(f'*** {err} ***')
                return []

        return [str(i) for i in
                sorted(parquet_ds.collect(EQUIPMENT_INSTANCE_ID_COL)
                       [EQUIPMENT_INSTANCE_ID_COL].unique())]

    def load_by_date(self,
                     date: str, to_date: Optional[str] = None,
                     equipment_instance_id: Optional[str] = None) \
            -> ParquetDataset:
        """Load equipment data by date(s)."""
        parquet_ds: ParquetDataset = self.load()

        try:
            parquet_ds: ParquetDataset = \
                parquet_ds.filterByPartitionKeys((DATE_COL, date, to_date)
                                                 if to_date
                                                 else (DATE_COL, date))

        except Exception as err:   # pylint: disable=broad-except
            ParquetDataset.classStdOutLogger().error(msg=str(err))

        if equipment_instance_id:
            parquet_ds: ParquetDataset = \
                parquet_ds.filter(f'{EQUIPMENT_INSTANCE_ID_COL} == '
                                  f'"{equipment_instance_id}"')

        return parquet_ds

    def load_by_equipment_instance_id_by_date(
            self,
            equipment_instance_id: str,
            date: str, to_date: Optional[str] = None) -> DataFrame:
        """Load equipment data by equipment instance ID and date(s)."""
        assert EQUIPMENT_DATA_TIMEZONE, \
            EnvironmentError(
                '*** H1ST_PMFP_EQUIPMENT_DATA_TIMEZONE env var not set ***')

        parquet_ds: ParquetDataset = \
            self.load().filter(f'{EQUIPMENT_INSTANCE_ID_COL} == '
                               f'"{equipment_instance_id}"')

        if date:
            parquet_ds: ParquetDataset = \
                parquet_ds.filterByPartitionKeys((DATE_COL, date, to_date)
                                                 if to_date
                                                 else (DATE_COL, date))

        return (parquet_ds.collect()
                .drop(columns=[EQUIPMENT_INSTANCE_ID_COL, DATE_COL],
                      inplace=False,
                      errors='raise')
                .sort_values(by=DATE_TIME_COL,
                             axis='index',
                             ascending=True,
                             inplace=False,
                             kind='quicksort',
                             na_position='last')
                .set_index(keys=DATE_TIME_COL,
                           drop=True,
                           append=False,
                           inplace=False,
                           verify_integrity=True)
                .tz_localize('UTC')
                .tz_convert(EQUIPMENT_DATA_TIMEZONE)
                .tz_localize(None))
