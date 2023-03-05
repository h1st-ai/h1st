"""Time-Series-DL-based knowledge generalizers."""


from __future__ import annotations

from functools import cached_property
import math
import pickle
from tempfile import NamedTemporaryFile
from typing import Optional, Union
from typing import Dict, List, Set, Tuple   # Py3.9+: use built-ins

from imblearn.over_sampling import RandomOverSampler
import joblib
from numpy import expand_dims
from pandas import DataFrame, Series
from scipy.stats.stats import hmean
from sklearn.metrics import precision_recall_curve
from sklearn.neural_network import MLPClassifier
from ruamel import yaml

from h1st.utils.data_proc import (PandasFlatteningSubsampler,
                                  PandasMLPreprocessor,
                                  ParquetDataset)
from h1st.utils.data_proc._abstract import ColsType
from h1st.utils.iter import to_iterable
from h1st.utils.path import add_cwd_to_py_path
from h1st.utils import fs, s3

from h1st.contrib.pmfp.data_mgmt import (EquipmentParquetDataSet,
                                         EQUIPMENT_INSTANCE_ID_COL, DATE_COL)
from h1st.contrib.pmfp.models.base import BaseFaultPredictor, H1ST_MODELS_DIR_PATH   # noqa: E501
from h1st.contrib.pmfp.models.oracle.teacher.base import BaseFaultPredTeacher


N_MINUTES_PER_DAY: int = 24 * 60


_ON_S3: bool = (isinstance(H1ST_MODELS_DIR_PATH, str) and
                H1ST_MODELS_DIR_PATH.startswith('s3://'))


class TimeSeriesDLFaultPredStudentModeler:
    """Time-Series-DL-based Fault Prediction k-gen ("student") modeler."""

    def __init__(self, teacher: BaseFaultPredTeacher,
                 input_cat_cols: Optional[ColsType],
                 input_num_cols: Optional[ColsType],
                 input_subsampling_factor: int,
                 input_n_rows_per_day: int,
                 date_range: Tuple[str, str]):
        # pylint: disable=super-init-not-called,too-many-arguments
        """Init Time-Series-DL-based student modeler."""
        self.teacher: BaseFaultPredTeacher = teacher
        self.general_type: str = teacher.general_type
        self.unique_type_group: str = teacher.unique_type_group

        self.input_cat_cols: Set[str] = (to_iterable(input_cat_cols,
                                                     iterable_type=set)
                                         if input_cat_cols
                                         else set())
        self.input_num_cols: Set[str] = (to_iterable(input_num_cols,
                                                     iterable_type=set)
                                         if input_num_cols
                                         else set())
        self.input_subsampling_factor: int = input_subsampling_factor
        self.input_n_rows_per_day: int = input_n_rows_per_day

        self.date_range: Tuple[str, str] = date_range

    def build_model(self, *,
                    hidden_layer_compress_factor: int = 10,
                    l2_regularization_factor: float = 3e0,
                    # *** HAND-TUNED TO COMBAT OVER-FITTING ***
                    # (target Prec & Recall of 70-80% against Teacher labels)
                    random_seed: Optional[int] = None) \
            -> TimeSeriesDLFaultPredStudent:
        # pylint: disable=arguments-differ,too-many-locals
        """Fit Knowledge Generalizer ("Student") model."""
        parquet_ds: ParquetDataset = (
            EquipmentParquetDataSet(general_type=self.general_type,
                                    unique_type_group=self.unique_type_group)
            .load()
            .filterByPartitionKeys(
                (DATE_COL, *self.date_range)
            )[(EQUIPMENT_INSTANCE_ID_COL, DATE_COL) +
              tuple(self.input_cat_cols) + tuple(self.input_num_cols)])

        parquet_ds.cacheLocally()

        parquet_ds, preprocessor = parquet_ds.preprocForML(
            *self.input_cat_cols, *self.input_num_cols,
            forceCat=self.input_cat_cols, forceNum=self.input_num_cols,
            returnPreproc=True)

        flattening_subsampler: PandasFlatteningSubsampler = \
            PandasFlatteningSubsampler(columns=tuple(preprocessor.sortedPreprocCols),   # noqa: E501
                                       everyNRows=self.input_subsampling_factor,   # noqa: E501
                                       totalNRows=self.input_n_rows_per_day)

        parquet_ds: ParquetDataset = parquet_ds.map(
            lambda df: (df.groupby(by=[EQUIPMENT_INSTANCE_ID_COL, DATE_COL],
                                   axis='index',
                                   level=None,
                                   as_index=True,   # group labels as index
                                   sort=False,   # better performance
                                   # when `apply`ing: add group keys to index?
                                   group_keys=False,
                                   # squeeze=False,   # deprecated
                                   observed=False,
                                   dropna=True)
                        .apply(func=flattening_subsampler, padWithLastRow=True)))   # noqa: E501

        parquet_ds.stdOutLogger.info(msg='Featurizing into Pandas DF...')
        df: DataFrame = parquet_ds.collect()
        parquet_ds.stdOutLogger.info(
            msg='Featurized into Pandas DF with:'
                f'\n{len(df.columns):,} Columns:\n{df.columns}'
                f'\nand Index:\n{df.index}')

        print('Getting Teacher Labels...')
        from_date, to_date = self.date_range
        teacher_predicted_faults_series: Series = \
            self.teacher.batch_process(date=from_date, to_date=to_date)
        teacher_predicted_faults_series.mask(
            cond=teacher_predicted_faults_series.isnull(),
            other=False,
            inplace=True,
            axis='index',
            level=None)
        teacher_predicted_faults_series.name = 'FAULT'
        print(teacher_predicted_faults_series)

        print('Joining Teacher Labels to Unlabeled Features...')
        df: DataFrame = df.join(other=teacher_predicted_faults_series, on=None,
                                how='left', lsuffix='', rsuffix='', sort=False)

        print(f'TRAINING ON {(n_rows := len(df)):,} ROWS w/ FAULT INCIDENCE = '
              f'{100 * teacher_predicted_faults_series.sum() / n_rows:,.1f}%...')   # noqa: E501
        transformed_cols: List[str] = flattening_subsampler.transformedCols
        print(f'{(n_cols := len(transformed_cols)):,} Columns')

        n_fwd_transforms: int = round(number=math.log(n_cols,
                                                      hidden_layer_compress_factor),   # noqa: E501
                                      ndigits=None)
        hidden_layer_sizes: Tuple[int] = \
            tuple(hidden_layer_compress_factor ** i
                  for i in reversed(range(1, n_fwd_transforms)))
        print(f'Hidden Layer Sizes: {hidden_layer_sizes}')
        print(f'L2 Weight Regularization Factor: {l2_regularization_factor}')

        native_skl_mlp_classifier: MLPClassifier = MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            # tuple, length = n_layers - 2, default=(100,)
            # The ith element represents the number of neurons
            # in the ith hidden layer.

            activation='tanh',
            # {‘identity’, ‘logistic’, ‘tanh’, ‘relu’}, default=’relu’
            # Activation function for the hidden layer.
            # - ‘identity’, no-op activation,
            # useful to implement linear bottleneck, returns f(x) = x
            # - ‘logistic’, the logistic sigmoid function,
            # returns f(x) = 1 / (1 + exp(-x)).
            # - ‘tanh’, the hyperbolic tan function, returns f(x) = tanh(x).
            # - ‘relu’, the rectified linear unit function,
            # returns f(x) = max(0, x)

            solver='adam',
            # {‘lbfgs’, ‘sgd’, ‘adam’}, default=’adam’
            # The solver for weight optimization.
            # - ‘lbfgs’ is an optimizer in the family of quasi-Newton methods.
            # - ‘sgd’ refers to stochastic gradient descent.
            # - ‘adam’ refers to a stochastic gradient-based optimizer
            # proposed by Kingma, Diederik, and Jimmy Ba
            # Note: The default solver ‘adam’ works pretty well on relatively
            # large datasets (with thousands of training samples or more)
            # in terms of both training time and validation score.
            # For small datasets, however, ‘lbfgs’ can converge faster
            # and perform better.

            alpha=l2_regularization_factor,
            # float, default=0.0001
            # L2 penalty (regularization term) parameter.

            batch_size='auto',
            # int, default=’auto’
            # Size of minibatches for stochastic optimizers.
            # If the solver is ‘lbfgs’, the classifier will not use minibatch.
            # When set to “auto”, batch_size=min(200, n_samples).

            # learning_rate='constant',
            # {‘constant’, ‘invscaling’, ‘adaptive’}, default=’constant’
            # Learning rate schedule for weight updates.
            # - ‘constant’ is a constant learning rate
            # given by ‘learning_rate_init’.
            # - ‘invscaling’ gradually decreases the learning rat at each
            # time step ‘t’ using an inverse scaling exponent of ‘power_t’.
            # effective_learning_rate = learning_rate_init / pow(t, power_t)
            # - ‘adaptive’ keeps the learning rate constant to
            # ‘learning_rate_init’ as long as training loss keeps decreasing.
            # Each time two consecutive epochs fail to decrease training loss
            # by at least tol, or fail to increase validation score by at least
            # tol if ‘early_stopping’ is on, the current learning rate
            # is divided by 5.
            # Only used when solver='sgd'.

            learning_rate_init=1e-3,
            # float, default=0.001
            # The initial learning rate used.
            # It controls the step-size in updating the weights.
            # Only used when solver=’sgd’ or ‘adam’.

            # power_t=0.5,
            # float, default=0.5
            # The exponent for inverse scaling learning rate.
            # It is used in updating effective learning rate
            # when the learning_rate is set to ‘invscaling’.
            # Only used when solver=’sgd’.

            max_iter=10 ** 3,
            # int, default=200
            # Maximum number of iterations.
            # The solver iterates until convergence (determined by ‘tol’)
            # or this number of iterations.
            # For stochastic solvers (‘sgd’, ‘adam’) note that this determines
            # the number of epochs (how many times each data point
            # will be used), not the number of gradient steps.

            shuffle=True,
            # bool, default=True
            # Whether to shuffle samples in each iteration.
            # Only used when solver=’sgd’ or ‘adam’.

            random_state=random_seed,
            # int, RandomState instance, default=None
            # Determines random number generation for weights and bias
            # initialization, train-test split if early stopping is used, and
            # batch sampling when solver=’sgd’ or ‘adam’. Pass an int for
            # reproducible results across multiple function calls.

            tol=1e-4,
            # float, default=1e-4
            # Tolerance for the optimization.
            # When the loss or score is not improving by at least tol
            # for n_iter_no_change consecutive iterations,
            # unless learning_rate is set to ‘adaptive’,
            # convergence is considered to be reached and training stops.

            verbose=True,
            # bool, default=False
            # Whether to print progress messages to stdout.

            warm_start=False,
            # bool, default=False
            # When set to True, reuse the solution of the previous call to fit
            # as initialization, otherwise, just erase the previous solution.

            # momentum=0.9,
            # float, default=0.9
            # Momentum for gradient descent update. Should be between 0 and 1.
            # Only used when solver=’sgd’.

            # nesterovs_momentum=True,
            # bool, default=True
            # Whether to use Nesterov’s momentum.
            # Only used when solver=’sgd’ and momentum > 0.

            early_stopping=True,
            # bool, default=False
            # Whether to use early stopping to terminate training
            # when validation score is not improving.
            # If set to true, it will automatically set aside 10% of training
            # data as validation and terminate training when validation score
            # is not improving by at least tol for n_iter_no_change consecutive
            # epochs. The split is stratified, except in a multilabel setting.
            # If early stopping is False, then the training stops when the
            # training loss does not improve by more than tol for
            # n_iter_no_change consecutive passes over the training set.
            # Only effective when solver=’sgd’ or ‘adam’.

            validation_fraction=0.32,
            # float, default=0.1
            # The proportion of training data to set aside as validation set
            # for early stopping. Must be between 0 and 1.
            # Only used if early_stopping is True.

            beta_1=0.9,
            # float, default=0.9
            # Exponential decay rate for estimates of first moment vector
            # in adam, should be in [0, 1).
            # Only used when solver=’adam’.

            beta_2=0.999,
            # float, default=0.999
            # Exponential decay rate for estimates of second moment vector
            # in adam, should be in [0, 1).
            # Only used when solver=’adam’.

            epsilon=1e-08,
            # float, default=1e-8
            # Value for numerical stability in adam.
            # Only used when solver=’adam’.

            n_iter_no_change=10 ** 2,
            # int, default=10
            # Maximum number of epochs to not meet tol improvement.
            # Only effective when solver=’sgd’ or ‘adam’.

            # max_fun=15000,
            # Only used when solver=’lbfgs’.
            # Maximum number of loss function calls.
            # The solver iterates until convergence (determined by ‘tol’),
            # number of iterations reaches max_iter, or this number of loss
            # function calls. Note that number of loss function calls will be
            # greater than or equal to the number of iterations.
        )

        x_resampled, y_resampled = (RandomOverSampler(sampling_strategy='minority',   # noqa: E501
                                                      random_state=random_seed,
                                                      shrinkage=None)
                                    .fit_resample(X=df[transformed_cols].values,   # noqa: E501
                                                  y=df.FAULT.astype(dtype=int,
                                                                    copy=True,
                                                                    errors='raise')   # noqa: E501
                                                  ))

        print(f'Class-Balanced Training Data Set with {len(y_resampled):,} Samples')   # noqa: E501

        native_skl_mlp_classifier.fit(X=x_resampled, y=y_resampled)

        student_model: TimeSeriesDLFaultPredStudent = \
            TimeSeriesDLFaultPredStudent(
                teacher=self.teacher,
                input_cat_cols=self.input_cat_cols,
                input_num_cols=self.input_num_cols,
                input_subsampling_factor=self.input_subsampling_factor,
                input_n_rows_per_day=self.input_n_rows_per_day,
                preprocessor=preprocessor,
                native_obj=native_skl_mlp_classifier,
                decision_threshold=.5)   # tune later

        student_model.save()

        return student_model


class TimeSeriesDLFaultPredStudent(BaseFaultPredictor):
    # pylint: disable=too-many-ancestors
    """Time-Series-DL-based knowledge generalizer ("student") model class."""

    def __init__(self, teacher: BaseFaultPredTeacher,

                 input_cat_cols: Optional[ColsType],
                 input_num_cols: Optional[ColsType],
                 input_subsampling_factor: int, input_n_rows_per_day: int,

                 preprocessor: PandasMLPreprocessor,

                 native_obj: MLPClassifier,

                 decision_threshold: float,

                 _version: Optional[str] = None):
        # pylint: disable=too-many-arguments
        """Init Time-Series-DL-based k-gen ("student") model."""
        super().__init__(general_type=teacher.general_type,
                         unique_type_group=teacher.unique_type_group,
                         version=_version)

        self.version: str = f'{teacher.name}---{type(self).__name__}--{self.version}'  # noqa: E501

        self.teacher: BaseFaultPredTeacher = teacher

        # input params
        self.input_cat_cols: Set[str] = (to_iterable(input_cat_cols,
                                                     iterable_type=set)
                                         if input_cat_cols
                                         else set())
        self.input_num_cols: Set[str] = (to_iterable(input_num_cols,
                                                     iterable_type=set)
                                         if input_num_cols
                                         else set())
        self.input_subsampling_factor: int = input_subsampling_factor
        self.input_n_rows_per_day: int = input_n_rows_per_day

        # preprocessing params
        self.preprocessor: PandasMLPreprocessor = preprocessor

        # native model
        self.native_obj: MLPClassifier = native_obj

        # postprocessing params
        self.decision_threshold: float = decision_threshold

    @cached_property
    def class_url(self) -> str:
        """Return model class's global dir URL."""
        return f'{H1ST_MODELS_DIR_PATH}/{type(self).__name__}'

    @cached_property
    def instance_url(self) -> str:
        """Return model instance's global dir URL."""
        return f'{self.class_url}/{self.version}'

    def __repr__(self) -> str:
        """Return string repr."""
        return (f'{self.unique_type_group} '
                'Time-Series-DL-based Knowledge Generalizer ("Student") Model '
                f'w/ Decision Threshold {self.decision_threshold:.3f} '
                f'@ {self.instance_url}')

    @cached_property
    def input_params_url(self) -> str:
        """Return model's input parameters URL."""
        return f'{self.instance_url}/input-params.yaml'

    @cached_property
    def preproc_params_url(self) -> str:
        """Return model's preprocessing parameters URL."""
        return f'{self.instance_url}/preproc-params.yaml'

    @cached_property
    def native_obj_url(self) -> str:
        """Return model's native object URL."""
        return f'{self.instance_url}/native-obj.pkl'

    @cached_property
    def postproc_params_url(self) -> str:
        """Return model's output parameters URL."""
        return f'{self.instance_url}/postproc-params.yaml'

    def save(self):
        """Save model params & native object."""
        # save input params
        with NamedTemporaryFile(mode='wt',
                                buffering=-1,
                                encoding='utf-8',
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=False,
                                errors=None) as input_params_tmp_file:
            yaml.safe_dump(data={'cat-cols': self.input_cat_cols,
                                 'num-cols': self.input_num_cols,
                                 'subsampling-factor': self.input_subsampling_factor,   # noqa: E501
                                 'n-rows-per-day': self.input_n_rows_per_day},
                           stream=input_params_tmp_file,
                           default_style=None,
                           default_flow_style=False,
                           encoding='utf-8',
                           explicit_start=None,
                           explicit_end=None,
                           version=None,
                           tags=None,
                           canonical=False,
                           indent=2,
                           width=100,
                           allow_unicode=True,
                           line_break=None)
        if _ON_S3:
            s3.mv(from_path=input_params_tmp_file.name,
                  to_path=self.input_params_url,
                  is_dir=False, quiet=False)

        else:
            fs.mv(from_path=input_params_tmp_file.name,
                  to_path=self.input_params_url,
                  hdfs=False, is_dir=False)

        # save preprocessing params
        with NamedTemporaryFile(mode='wb',
                                buffering=-1,
                                encoding=None,
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=False,
                                errors=None) as preproc_params_tmp_file:
            self.preprocessor.to_yaml(path=preproc_params_tmp_file.name)

        if _ON_S3:
            s3.mv(from_path=preproc_params_tmp_file.name,
                  to_path=self.preproc_params_url,
                  is_dir=False, quiet=False)

        else:
            fs.mv(from_path=preproc_params_tmp_file.name,
                  to_path=self.preproc_params_url,
                  hdfs=False, is_dir=False)

        # save native object
        with NamedTemporaryFile(mode='wb',
                                buffering=-1,
                                encoding=None,
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=False,
                                errors=None) as native_obj_tmp_file:
            joblib.dump(value=self.native_obj,
                        filename=native_obj_tmp_file.name,
                        compress=9,
                        protocol=pickle.HIGHEST_PROTOCOL,
                        cache_size=None)

        if _ON_S3:
            s3.mv(from_path=native_obj_tmp_file.name,
                  to_path=self.native_obj_url,
                  is_dir=False, quiet=False)

        else:
            fs.mv(from_path=native_obj_tmp_file.name,
                  to_path=self.native_obj_url,
                  hdfs=False, is_dir=False)

        # save postprocessing params
        with NamedTemporaryFile(mode='wt',
                                buffering=-1,
                                encoding='utf-8',
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=False,
                                errors=None) as postproc_params_tmp_file:
            yaml.safe_dump(data={'decision-threshold': self.decision_threshold},  # noqa: E501
                           stream=postproc_params_tmp_file,
                           default_style=None,
                           default_flow_style=False,
                           encoding='utf-8',
                           explicit_start=None,
                           explicit_end=None,
                           version=None,
                           tags=None,
                           canonical=False,
                           indent=2,
                           width=100,
                           allow_unicode=True,
                           line_break=None)

        if _ON_S3:
            s3.mv(from_path=postproc_params_tmp_file.name,
                  to_path=self.postproc_params_url,
                  is_dir=False, quiet=False)

        else:
            fs.mv(from_path=postproc_params_tmp_file.name,
                  to_path=self.postproc_params_url,
                  hdfs=False, is_dir=False)

        print(f'SAVED: {self}')

    @classmethod
    def load(cls, version: str) -> TimeSeriesDLFaultPredStudent:
        # pylint: disable=too-many-locals
        """Load Time-Series-DL-based k-gen ("student") model."""
        add_cwd_to_py_path()

        # pylint: disable=import-error,import-outside-toplevel
        import ai.models

        teacher_name, student_str = version.split('---')

        teacher_class_name, teacher_version = teacher_name.split('--')
        teacher_class = getattr(ai.models, teacher_class_name)
        teacher: BaseFaultPredTeacher = teacher_class.load(version=teacher_version)   # noqa: E501

        _student_class_name, _student_version = student_str.split('--')

        student: TimeSeriesDLFaultPredStudent = cls(
            teacher=teacher,

            # params to load in subsequent steps below
            input_cat_cols=None, input_num_cols=None,
            input_subsampling_factor=None,
            input_n_rows_per_day=None,
            preprocessor=None,
            native_obj=None,
            decision_threshold=None,

            _version=_student_version)

        # load input params
        with NamedTemporaryFile(mode='rt',
                                buffering=-1,
                                encoding='utf-8',
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=True,
                                errors=None) as input_params_tmp_file:
            if _ON_S3:
                s3.cp(from_path=student.input_params_url,
                      to_path=input_params_tmp_file.name,
                      is_dir=False, quiet=False)

            else:
                fs.cp(from_path=student.input_params_url,
                      to_path=input_params_tmp_file.name,
                      hdfs=False, is_dir=False)

            # pylint: disable=consider-using-with
            d: Dict[str, Union[List[str], int]] = \
                yaml.safe_load(stream=open(file=input_params_tmp_file.name,
                                           mode='rt', encoding='utf-8'),
                               version=None)

            student.input_cat_cols = d['cat-cols']
            student.input_num_cols = d['num-cols']
            student.input_subsampling_factor = d.get('subsampling-factor', 1)
            student.input_n_rows_per_day = d.get('n-rows-per-day', N_MINUTES_PER_DAY)   # noqa: E501

        # load preprocessing params
        with NamedTemporaryFile(mode='rt',
                                buffering=-1,
                                encoding='utf-8',
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=True,
                                errors=None) as preproc_params_tmp_file:
            if _ON_S3:
                s3.cp(from_path=student.preproc_params_url,
                      to_path=preproc_params_tmp_file.name,
                      is_dir=False, quiet=False)

            else:
                fs.cp(from_path=student.preproc_params_url,
                      to_path=preproc_params_tmp_file.name,
                      hdfs=False, is_dir=False)

            student.preprocessor = \
                PandasMLPreprocessor.from_yaml(path=preproc_params_tmp_file.name)   # noqa: E501

        # load native object
        with NamedTemporaryFile(mode='rb',
                                buffering=-1,
                                encoding=None,
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=True,
                                errors=None) as native_obj_tmp_file:
            if _ON_S3:
                s3.cp(from_path=student.native_obj_url,
                      to_path=native_obj_tmp_file.name,
                      is_dir=False, quiet=False)

            else:
                fs.cp(from_path=student.native_obj_url,
                      to_path=native_obj_tmp_file.name,
                      hdfs=False, is_dir=False)

            student.native_obj = joblib.load(filename=native_obj_tmp_file.name)

        with NamedTemporaryFile(mode='rt',
                                buffering=-1,
                                encoding='utf-8',
                                newline=None,
                                suffix=None,
                                prefix=None,
                                dir=None,
                                delete=True,
                                errors=None) as postproc_params_tmp_file:
            if _ON_S3:
                s3.cp(from_path=student.postproc_params_url,
                      to_path=postproc_params_tmp_file.name,
                      is_dir=False, quiet=False)

            else:
                fs.cp(from_path=student.postproc_params_url,
                      to_path=postproc_params_tmp_file.name,
                      hdfs=False, is_dir=False)

            # pylint: disable=consider-using-with
            d: Dict[str, float] = yaml.safe_load(
                stream=open(file=postproc_params_tmp_file.name,
                            mode='rt', encoding='utf-8'),
                version=None)

            student.decision_threshold = d['decision-threshold']

        return student

    @property
    def flattening_subsampler(self) -> PandasFlatteningSubsampler:
        """Get instance's Pandas flattening subsampler."""
        return PandasFlatteningSubsampler(
            columns=tuple(self.preprocessor.sortedPreprocCols),
            everyNRows=self.input_subsampling_factor,
            totalNRows=self.input_n_rows_per_day)

    def predict(self,
                df_for_1_equipment_unit_for_1_day: DataFrame, /,
                return_binary: bool = True) -> Union[bool, float]:
        # pylint: disable=arguments-differ
        """Predict fault."""
        prob: float = self.native_obj.predict_proba(
            X=expand_dims(
                self.flattening_subsampler(
                    self.preprocessor(df_for_1_equipment_unit_for_1_day)).values,   # noqa: E501
                axis=0))[0, 1]

        return (prob > self.decision_threshold) if return_binary else prob

    def batch_predict(self,
                      parquet_ds: ParquetDataset, /,
                      return_binary: bool = True) -> Series:
        # pylint: disable=arguments-differ
        """Batch-Predict faults."""
        df: DataFrame = parquet_ds.map(
            self.preprocessor,
            lambda df: (df.groupby(by=[EQUIPMENT_INSTANCE_ID_COL, DATE_COL],
                                   axis='index',
                                   level=None,
                                   as_index=True,   # group labels as index
                                   sort=False,   # better performance
                                   # when `apply`ing: add group keys to index?
                                   group_keys=False,
                                   # squeeze=False,   # deprecated
                                   observed=False,
                                   dropna=True)
                        .apply(func=self.flattening_subsampler,
                               padWithLastRow=True))).collect()

        df.loc[:, 'FAULT'] = self.native_obj.predict_proba(X=df.values)[:, 1]

        return (df.FAULT > self.decision_threshold) if return_binary else df.FAULT   # noqa: E501

    def tune_decision_threshold(self, tuning_date_range: Tuple[str, str]):
        """Tune Model's decision threshold to maximize P-R harmonic mean."""
        tune_from_date, tune_to_date = tuning_date_range

        precision, recall, thresholds = \
            precision_recall_curve(
                y_true=((_y_true := self.teacher.batch_process(date=tune_from_date,   # noqa: E501
                                                               to_date=tune_to_date))   # noqa: E501
                        .mask(cond=_y_true.isnull(),
                              other=False,
                              inplace=False,
                              axis='index',
                              level=None)
                        .astype(dtype=bool, copy=True, errors='raise')),
                probas_pred=self.batch_process(date=tune_from_date,
                                               to_date=tune_to_date,
                                               return_binary=False))

        df: DataFrame = DataFrame(data=dict(threshold=list(thresholds) + [1],
                                            precision=precision, recall=recall))   # noqa: E501
        df.loc[:, 'pr_hmean'] = hmean(df[['precision', 'recall']], axis=1)
        best_pr_tradeoff_idx: int = df.pr_hmean.argmax(skipna=True)
        print('BEST PRECISION-RECALL TRADE-OFF:')
        self.decision_threshold: float = \
            float(df.threshold.iloc[best_pr_tradeoff_idx])
        print(f'- Decision Threshold: {self.decision_threshold:.3f}')
        print(f'- Precision: {df.precision.iloc[best_pr_tradeoff_idx]:.3f}')
        print(f'- Recall: {df.recall.iloc[best_pr_tradeoff_idx]:.3f}')
        print(f'- PR Harmonic Mean: {df.pr_hmean.iloc[best_pr_tradeoff_idx]:.3f}')   # noqa: E501

        self.save()
