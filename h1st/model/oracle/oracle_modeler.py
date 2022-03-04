from typing import Any, Dict, List
import pandas as pd
from h1st.model.ml_modeler import MLModeler

from h1st.model.modeler import Modeler
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.student import AdaBoostModeler, RandomForestModeler
from h1st.model.predictive_model import PredictiveModel
from h1st.model.ensemble.stack_ensemble_modeler import StackEnsembleModeler

class OracleModeler(Modeler):
    def __init__(self, teacher: PredictiveModel,
                 ensembler_modeler: Modeler,
                 student_modelers: List = [RandomForestModeler(), AdaBoostModeler()],
                 model_class = Oracle
                 ):
        self.teacher = teacher
        self.student_modelers = student_modelers
        self.ensembler_modeler = ensembler_modeler
        self.model_class = model_class
        self.stats = {}

    def build_model(self, data: Dict[str, Any] = None, features: List = None) -> Oracle:
        """
        Build the student and ensemble components.
        :param data: Unlabeled data.
        """
        self.stats['features'] = features
        # Generate features to get students' predictions
        train_data = self.model_class.generate_data({'X': data['unlabelled_data']}, self.teacher, self.stats)

        # Train the student model
        self.students = [student_modeler.build_model(train_data)
                         for student_modeler in self.student_modelers]

        # Train the ensembler
        labelled_data = data.get('labelled_data', None)

        if isinstance(self.ensembler_modeler, MLModeler) and labelled_data is None:
            raise ValueError('No data to train the machine-learning-based ensemble')

        if labelled_data is not None:
            ensembler_train_data = self.model_class.generate_data({'X': labelled_data['X_train']}, self.teacher, self.stats)
            ensembler_test_data = self.model_class.generate_data({'X': labelled_data['X_test']}, self.teacher, self.stats)
            student_preds_train_data = [pd.Series(student.predict(ensembler_train_data)['predictions']) for student in self.students]
            student_preds_test_data = [pd.Series(student.predict(ensembler_test_data)['predictions']) for student in self.students]
            ensembler_data = {'X_train': pd.concat(student_preds_train_data + 
                                                [ensembler_train_data['y']], axis=1),
                                    'y_train': labelled_data['y_train'],
                                    'X_test': pd.concat(student_preds_test_data + 
                                                [ensembler_test_data['y']], axis=1),
                                    'y_test': labelled_data['y_test'],
                                    }
        else:
            ensembler_data = None

        ensembler_model = self.ensembler_modeler.build_model(ensembler_data)
        oracle = self.model_class(self.teacher, self.students, ensembler_model)
        # Pass stats to the model
        if self.stats is not None:
            oracle.stats = self.stats.copy()

        return oracle
