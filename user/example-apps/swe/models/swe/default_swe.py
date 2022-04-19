import utils
from h1st.model.swe import SegmentedWorldEnsembleModeler, SegmentedWorldEnsemble
from h1st.model.swe import RandomForestClassifierModeler, MajorityVotingEnsembleModeler

'''
This is the user code of default SegmentedWorldEnsembleModeler which
use CombinationSegmentor as a default Segmentor.

'''
### 1. Load Data
data = utils.load_data() 

### 2. Provide segmentation_features
'''
User provides how to segment their data through segmentation_features. 
For each feature, user can provide a list of filters. Each filter can be 
a list or tuple.
  1. list - Feature should have one of the values in the list 
  2. tuple(start, end) - Feature should be in the range of [start: end). 
    If start or end is None, that means no lower or upper boundary in a range.
'''
segmentation_features = utils.load_segmentation_features('.ini file path')
segmentation_features = {
    'sepal_size': [(None, 18.5), (18.5, None)],
    'sepal_aspect_ratio': [(0, 0.65), (0.65, 1)],
    'species': [[0, 1]]
}

### 3. Instantiate SWE Modeler
swe_modeler = SegmentedWorldEnsembleModeler()

### 4. Build SWE
'''
input_data: Dict 
    Entire data for training the sub_models and ensembles of SWE. 
segmentation_features: Dict
    Explained above. 
segmentation_levels: List
    Number of features being used to create each segment. If level=1, then
    take a filter from only one featrue to create a segment. If level=2, then 
    take a filter from each feature and create a combined filter to create a 
    segment. To create a combined filter, do and operation between two filters.
    
    For example, given an above segmentation_features, if level=3, then you will
    have the following 4 segments.
        segment_1: (sepal_size, (None, 18.5)) & (sepal_aspect_ratio, (0, 0.65)) & (species, [0, 1])
        segment_2: (sepal_size, (None, 18.5)) & (sepal_aspect_ratio, (0.65, 1)) & (species, [0, 1])
        segment_3: (sepal_size, (18.5, None)) & (sepal_aspect_ratio, (0, 0.65)) & (species, [0, 1])
        segment_4: (sepal_size, (18.5, None)) & (sepal_aspect_ratio, (0.65, 1)) & (species, [0, 1])
    If level=1, then you will have the following 5 segments.
        segment_1: (sepal_aspect_ratio, (0, 0.65))
        segment_2: (sepal_aspect_ratio, (0.65, 1))
        segment_3: (sepal_size, (None, 18.5))
        segment_4: (sepal_size, (18.5, None))
        segment_5: (species, [0, 1])
min_data_size: 
    Number of data points in each segment should be larger than this value. 
    If not, ignore that segment or auto-merge it into other segment so that
    the total number data points in a merged segment is larger than min_data_size.  
sub_model_modeler:  
    User can use their own sub_model modeler, or use pre-built modeler, 
    such as RandomForestClassifierModeler.
ensemble_modeler:
    User can use their own ensemble modeler, or use pre-built modeler, 
    such as MajorityVotingEnsembleModeler.
'''
swe = swe_modeler.build_model(
    input_data=data,
    segmentation_features=segmentation_features,
    segmentation_levels=[1, 2],
    min_data_size=50, 
    sub_model_modeler=RandomForestClassifierModeler,
    ensemble_modeler=MajorityVotingEnsembleModeler
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

