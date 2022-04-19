from typing import Union, Dict, Tuple, List

import pandas as pd

from sub_model import MySubModelModeler, MyEnsembleModeler
import utils
from h1st.model.swe import SegmentedWorldEnsembleModeler, SegmentedWorldEnsemble, Segmentor

'''
This is the user code of custom SegmentedWorldEnsembleModeler which use 
custom MySegmentor, MySubModelModeler, and MyEnsembleModeler.
'''

### 1. Load Data
data = utils.load_data() 

### 2. Build Custom Segmentor
'''
User build a custom Segmentor that will be used to segment the entire dataset.
User should implement the following methods
1. segment(data: Dataframe or Dict, by: Dict) -> Dict:
    This method splits data using the by value. 
    This method returns two variables, segmented_data and filter_combinations. 
    Their format is like the following.
    - segmented_data: Dict[segment_name: str, data_segment: pd.DataFrame or Dict]
    - filter_combinations: Dict[segment_name: str, list_of_filters: List[(feature_name, filter)]] 
      Each filter can be a list or tuple.
        1. list - Feature should have one of the values in the list 
        2. tuple(start, end) - Feature should be in the range of [start: end). 
            If start or end is None, that means no lower or upper boundary in a range.
    The example of them are provided in MySegmentor class. 

2. identify_segment(data, filter_combinations):
    This method finds the proper segment of provided data and return its
    segment_name. When you use SWE in inference phase, based on this segment info, 
    you can select or give more weight on relevant models. If you implement this logic
    inside Ensemble itself, then you don't need to implement this method. 
'''
class MySegmentor(Segmentor):
    def segment(data: Union[pd.DataFrame, Dict]) -> Tuple[Dict]:
        segmented_data = {
            'segment_0': data_segment_0,
            'segment_1': data_segment_1
        }
        filter_combinations = {
            'segment_0': [('sepal_size', (None, 18.5)),('sepal_aspect_ratio', (None, 0.65))],
            'segment_1': [('sepal_size', (18.5, None)),('species', [0, 1])],
        }
        return (segmented_data, filter_combinations)
        
    def identify_segment(data: Union[pd.DataFrame, Dict], filter_combinations: Dict) -> List:
        segment_names = ['segment_0']
        return segment_names

### 3. Instantiate SWE Modeler
swe_modeler = SegmentedWorldEnsembleModeler()

### 4. Build SWE
'''
input_data: Dict 
    Entire data for training the sub_models and ensembles of SWE. 
sub_model_modeler:  
    User can use their own sub_model modeler, or use pre-built modeler, 
    such as RandomForestClassifierModeler.
ensemble_modeler:
    User can use their own ensemble modeler, or use pre-built modeler, 
    such as MajorityVotingEnsembleModeler.
segmentor:

'''
swe = swe_modeler.build_model(
    input_data=data,
    sub_model_modeler=MySubModelModeler,
    ensemble_modeler=MyEnsembleModeler,
    segmentor=MySegmentor()
)

### 5. Check evalutaion results
print(swe.metrics)

### 6. Persist SWE
swe.persist(swe, 'my_version')

### 7. Reload SWE in Application
swe = SegmentedWorldEnsemble().load_param('my_version')
swe.predict(data)


# ============= After merging model-refactoring branch into main branch

### 3. Instantiate SWE Modeler
swe_modeler = SegmentedWorldEnsemble.get_modeler()

### 4. Build SWE - same

### 5. Check evalutaion results - same

### 6. Persist SWE
swe_modeler.persist(swe, 'my_version')

### 7. Reload SWE in Application
swe = SegmentedWorldEnsemble().get_modeler().load('my_version')
swe.predict(data)

