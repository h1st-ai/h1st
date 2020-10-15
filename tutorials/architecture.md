H1st Architectural Overview
====

H1st comprises a Workbench (user interface) and an API framework.

## Objects

### Graph
An H1st Graph is essentially a flowchart. It is a directed graph describing an execution flow (and not a data flow). There may be conditionals and loops in an H1st Graph.

H1st Graphs describe both high-level business workflows, as well as low-level model-to-model execution flow.

### Node
Nodes are elements that connect to form a Graph. An H1st Node has inputs, outputs, and may contain within it a NodeContainable.

### NodeContainable
NodeContainables are anything that might be contained within a Node. Most often, what we see contained is a Model. A Graph is also a NodeContainables, so that H1st Graphs are hierarchical: a Graph may contain a sub-Graph and so on.

### Model
H1st Models are the workhorse of the entire framework. At the base, a Model is the simplest unit that “models” a behavior that takes some inputs, processes them, and emits some outputs.

#### ProcessModel
A ProcessModel mainly exists to distinguish between predictive and non-predictive models.
##### DataAnnotatingModel
A DataAnnotatingModel takes some data as inputs and annotates or labels them. They are mainly used to process training data for PredictiveModels.
##### DataGeneratingModel
A DataGeneratingModel takes some parameters as inputs, and outputs data used as training data for PredictiveModels.
##### DataAugmentingModel
A DataAugmentingModel is like a DataGeneratingModel, but used in the context of expanding or adding to some existing training data.

#### PredictiveModel
A PredictiveModel Is a Model that interpolates or extrapolates, more generally, it outputs inferences based on the parameters within it. The parameters may be externally set, or automatically learned from the data.
##### MLModel
An MLModel Is a PredictiveModel that gets its parameters via machine learning. It has a standardized API including methods such as load_data(), explore(), train(), predict(), evaluate() etc.
##### RuleBasedModel
A RuleBasedModel Is a PredictiveModel that follows Boolean logic at its core.
##### FuzzyLogicModel
A FuzzyLogicModel Is a PredictiveModel that uses fuzzy logic for its outputs.
##### KalmanFilterModel
A FuzzyLogicModel Is a PredictiveModel that uses Kalman filters for its inferences.




## Capabilities

### Trustable
Trustable is one of the most important capabilities of H1st objects, most notably, of H1st Models. It really comprises each of the capabilities below.

#### Auditable
To be trusted, an object (Model) must be Auditable. It means that the object self-records an audit trail of its provenance and decisions, so that authorized personnel can query the object with questions like, “When was this model trained? Who did it? What was the data it was trained with? What biases exist in that training data? What is the history of decisions made by this model and what were the corresponding input data?”

#### Describable
To be trusted, an object (Model) must at minimum be Describable. It means that the object is self-describing when queried, with information such as “What the intent of the model is, and how it is designed to achieve that intent?

#### Explainable
To be trusted, an object (Model) must also be Explainable. It means that authorized personnel can query the object with questions like, “What are the top 3 most important input features for this model? Why did this model make that particular decision in that way?”

#### Debiasable
To be trusted, an object (Model) must be Auditable. It means that authorized personnel can query the object with questions like, “When was this model trained? Who did it.”.

### Constituency
    DATA_SCIENTIST
    BUSINESS_MANAGER
    CUSTOMER
    USER
    CONSUMER
    REGULATOR
    LEGISLATOR
    ANY
    OTHER
    
### Aspect
    ACCOUNTABLE
    FUNCTIONAL
    OPERATIONAL
    ANY
    OTHER
