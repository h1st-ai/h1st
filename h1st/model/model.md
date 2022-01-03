
### Basic object model

```
@startuml

interface Modelable

Modeler -right- Modelable : produces >
Model .left.> Modelable : implements

Modeler : load_data() → dict
Modeler : explore_data()
Modeler : build_model() → Modelable
Modeler : evaluate_model() → dict

Model : persist()
Model : load_params()
Model : process() → Any

@enduml
```

### Basic Model hiearchy

```
@startuml
Class Model

PredictiveModel -up-> Model

MLModel -up->PredictiveModel
BooleanModel -up->PredictiveModel
RuleBasedModel -up->PredictiveModel
Oracle -up-> PredictiveModel

FuzzyLogicModel -up->RuleBasedModel
@enduml
```
