from typing import Dict, List

from sklearn.model_selection import train_test_split as sk_train_test_split

from h1st.model.modeler import Modeler
from h1st.model.ml_modeler import MLModeler
from .segmentor import Segmentor, CombinationSegmentor
from .swe import SegmentedWorldEnsemble
from .sub_model_modeler import RandomForestClassifierModeler
from .ensemble import MajorityVotingEnsemble

class SegmentedWorldEnsembleModeler(Modeler):
    def __init__(self, model_class=SegmentedWorldEnsemble):
        self.model_class = model_class
        self.stats = {}

    def train_test_split(self, data, test_size=0.4):
        sk_train_test_split(data, test_size)
        pass 

    def build_model(
        self,
        input_data: Dict, 
        segmentation_features: Dict, 
        segmentor: Segmentor = CombinationSegmentor, 
        sub_model_modeler: MLModeler = RandomForestClassifierModeler,
        ensembler_modeler: MLModeler = MajorityVotingEnsemble,
    ):
        # Check if data is in correct format
        if 'X_train' not in input_data:
            raise KeyError('X_train is not in your input_data')
        if 'y_train' not in input_data:
            raise KeyError('y_train is not in your input_data')
        if 'X_segmentation' not in input_data:
            raise KeyError('y_train is not in your input_data')                     

        # Segment data by segmentation_features
        segmented_data = segmentor.segment(data, by=segmentation_features)

        # Build sub_models (TODO: make it parallelized)
        sub_models = [sub_model_modeler.build_model(data) 
                           for data in segmented_data]

        # Prepare training data for Ensembler
        # Depending on the ensemble strategy, we should prepare the training data differently
        student_preds_train_data = [pd.Series(student.predict(ensembler_train_data)['predictions']) for student in self.sub_models]
        student_preds_test_data = [pd.Series(student.predict(ensembler_test_data)['predictions']) for student in self.sub_models]
        ensembler_data = {
            'X_train': pd.concat(student_preds_train_data + [ensembler_train_data['y']], axis=1),
            'y_train': labeled_data['y_train'],
            'X_test': pd.concat(student_preds_test_data + [ensembler_test_data['y']], axis=1),
            'y_test': labeled_data['y_test'],
        }

        # Build Ensembler
        ensembler = ensembler_modeler.build_model(ensembler_data)

        # Build SWE
        swe = self.model_class(sub_models, ensembler)
        
        # Pass stats to the model
        if self.stats is not None:
            swe.stats = self.stats.copy()

        return swe