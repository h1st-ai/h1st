import utils
from h1st.model.kswe import KSWEModeler, KSWE
from h1st.model.kswe import RandomForestClassifierModeler, MajorityVotingEnsembleModeler

'''
This is the user code of default KSWEModeler which use CombinationSegmentor 
as a default Segmentor. The overall process is like the following. 
1. load data
2. provide segmentation_features that explains what features users want to
  use to generate data segments from the original data
3. build sub_model_modeler and ensemble_modeler or just use pre-built
  modelers from h1st
4. Pass them to KSWEModeler.build_model() method. 
5. Check (auto-generated) evaluation results and persist KSWE if the evaluation
    results is good enough. Otherwise, iterate the fine-tuning process. 
6. Load and use KSWE in inference application



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
    'sepal_size': [(0, 18.5), (18.5, None)],
    'sepal_aspect_ratio': [(0, 0.65), (0.65, 1)],
    'species': [[0, 1]]
}

### 3. Instantiate KSWE Modeler
kswe_modeler = KSWEModeler()

### 4. Build KSWE
'''
input_data: Dict 
    Entire data for training/evaluating the sub_models and ensembles of KSWE. 
segmentation_features: Dict
    Explained above. 
min_segment_size: 
    Number of data points in each segment should be larger than this value. 
    If not, ignore that segment or auto-merge it into other segment so that
    the total number data points in a merged segment is larger than min_segment_size.  
sub_model_modeler:  
    User can use their own sub_model modeler, or use pre-built modeler, 
    such as RandomForestClassifierModeler.
ensemble_modeler:
    User can use their own ensemble modeler, or use pre-built modeler, 
    such as MajorityVotingEnsembleModeler.
'''
kswe = kswe_modeler.build_model(
    input_data=data,
    segmentation_features=segmentation_features,
    min_segment_size=50, 
    sub_model_modeler=RandomForestClassifierModeler,
    ensemble_modeler=MajorityVotingEnsembleModeler
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

