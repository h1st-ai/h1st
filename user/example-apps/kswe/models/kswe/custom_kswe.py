from typing import Union, Dict, Tuple, List

import pandas as pd

from sub_model import MySubModelModeler, MyEnsembleModeler
import utils
from h1st.model.kswe import KSWEModeler, KSWE
from h1st.model.model import Model
'''
This is the user code of custom KSWEModeler. We demonstrate here how users can 
fully customize the segmentor for segmenting data and use it in KSWEModeler. 
If users want to customize SubModel and Ensemble, they can use their
customized SubModelModeler, and EnsembleModeler. We will show you how to use
them in KSWE as well. 
In Summary, overall process is like the following. 
1. Load entire data
2. Build custom Segmentor, SubModelModeler, and EnsembleModeler
3. Pass them to KSWEModeler.build_model() method. 
4. Check (auto-generated) evaluation results and persist KSWE if the evaluation
    results is good enough. Otherwise, iterate the fine-tuning process. 
5. Load and use KSWE in inference application
'''

### 1. Load Data
data = utils.load_data() 

### 2. Build Custom Segmentor
'''
User build a custom Segmentor that will be used to segment the entire dataset.
User should implement the following two methods
1. segment(data: Dataframe or Dict, by: Dict) -> Dict:
    This is where users can implement data segmentation logics. Using your 
    segmentation_logics, this method generates segmentation_results which includes
    data segments with their names.
    This method should return two variables, segmentation_results and segmentation_logics.
    
    Their format is like the following.
    - segmentation_results: Dict[segment_name: str, data_segment: Union[pd.DataFrame, Dict]]
    - segmentation_logics: Dict[segment_name: str, list_of_segmentation_logic: List[(feature_name, logic)]] 
      Each logic can be a list or tuple.
        1. list - Make a segment that has one of the values in the list in the feature column
        2. tuple(start, end) - Make a segment whose values of feature column are in the range of [start: end). 
            If start or end is None, that means no lower or upper boundary in a range.
    The example of them are provided in MySegmentor class. 

2. identify_segment(data, segmentation_logics):
    This method finds the proper segment of provided data and return its
    segment_name. When you use KSWE in inference phase, based on this segment info, 
    you can select or give more weight on relevant models. If you implement this logic
    inside Ensemble itself, then you don't need to implement this method. 
'''
class MySegmentor(Model):
    def process(data: Union[pd.DataFrame, Dict]) -> Tuple[Dict]:
        segmentation_results = {
            'segment_0': data_segment_0,
            'segment_1': data_segment_1
        }
        segmentation_logics = {
            'segment_0': [('sepal_size', (2, 18.5)),('species', [0, 1])],
            'segment_1': [('sepal_size', (18.5, 30)),('species', [0, 1])],
        }
        return (segmentation_results, segmentation_logics)

    def identify_segment(data: Union[pd.DataFrame, Dict], segmentation_logics: Dict) -> List:
        segment_names = ['segment_0']
        return segment_names

### 3. Instantiate KSWEModeler
kswe_modeler = KSWEModeler()

### 4. Build KSWE
'''
input_data: Dict 
    Entire data for training the sub_models and ensembles of KSWE. 
sub_model_modeler:  
    User can use their own sub_model modeler, or use pre-built modeler, 
    such as RandomForestClassifierModeler.
ensemble_modeler:
    User can use their own ensemble modeler, or use pre-built modeler, 
    such as MajorityVotingEnsembleModeler.
segmentor:
'''
kswe = kswe_modeler.build_model(
    input_data=data,
    sub_model_modeler=MySubModelModeler,
    ensemble_modeler=MyEnsembleModeler,
    segmentor=MySegmentor()
)

### 5. Check evalutaion results
print(kswe.metrics)

### 6. Persist KSWE
kswe.persist(kswe, 'my_version')

### 7. Reload KSWE in Application
kswe = KSWE().load_param('my_version')
kswe.predict(data)


# ============= After merging model-refactoring branch into main branch

### 3. Instantiate KSWE Modeler
kswe_modeler = KSWE.get_modeler()

### 4. Build KSWE - same

### 5. Check evalutaion results - same

### 6. Persist KSWE
kswe_modeler.persist(kswe, 'my_version')

### 7. Reload KSWE in Application
kswe = KSWE().get_modeler().load('my_version')
kswe.predict(data)

