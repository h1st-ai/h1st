H1st Object Model
=================

**This does not need to be so exhaustive. Include only the primary concepts. Leave the details for the API docs**

Graph
#####
An H1st Graph is essentially a flowchart, modeling a real-world workflow. It is a directed graph describing an execution flow (and not a data flow). There may be conditionals and loops in an H1st Graph.

H1st Graphs can describe both high-level business workflows, as well as low-level model-to-model execution flow.

Node
####
Nodes are elements that connect to form a Graph. An H1st Node has inputs, outputs, and may contain within it a NodeContainable.

NodeContainable
###############
NodeContainables are anything that might be contained within a Node. Most often, what we see contained is a Model. A Graph is also a NodeContainable, so that H1st Graphs are hierarchical: a Graph may contain a sub-Graph and so on.

Model
#####
H1st Models are the workhorse of the entire framework. At the base, a Model is the simplest unit that “models” a behavior. That is, it takes some input, processes, analyzes or transforms that input, and emits some output.

ProcessModel
############
A ProcessModel mainly exists to distinguish between predictive and non-predictive models.

DataAnnotatingModel
###################
A DataAnnotatingModel takes in some data and outputs annotation or labels. They are mainly used to process training data for MLModels.

DataGeneratingModel
###################
A DataGeneratingModel takes some parameters as inputs, and outputs synthetic data that can be used as training data for PredictiveModels or MLModels.

DataAugmentingModel
###################
A DataAugmentingModel is like a DataGeneratingModel, but used in the context of expanding or adding to some existing training data.

PredictiveModel
###############
A PredictiveModel is a Model that interpolates or extrapolates, more generally, outputs inferences based on the parameters within it. The parameters may be externally set, implemented as rules within the Model, or automatically learned from the data. It extends the root Model adding in a predict() function to support standard inference schema, but this function simply aliases the Model.process() function, which should to implemented by the user to enable Model functionality.

MLModel
#######
An MLModel is a PredictiveModel that gets its parameters via machine learning. It provides a standardized API with predict(), persist() and load_param() functions. User's extending the MLModel need only implment a process() function, and the framework with enable model storage and loading. These models also have `stats` and `metrics` attributes which are persisted along with the model and store model metadata and evaluation metrics.

RuleBasedModel
##############
A RuleBasedModel is a PredictiveModel that follows Boolean logic at its core.

FuzzyModel
###############
A FuzzyModel is a PredictiveModel that uses fuzzy logic for its outputs.

KalmanFilterModel
#################
A KalmanFilterModel is a PredictiveModel that uses Kalman filters for its inferences.

Modeler
#######
Many models, especially those who parameters are inferred from data, require training in order to reach a usuable form. These models should have an accompanying Modeler to handle all processes related to Model creation. In the simplest case a modeler must implement a build() function which outputs a trained H1st Model, but can also include processes sucha as data loading, preprocessing, train-test splits, and model evaluation. In this way, the Operation and Creation processes are kept distinctly separate, and as new data is generated, Modelers can update Model in separate production processes so as not to interfere with system operation. 

H1st Object Capabilities
########################

Trustable
#########
Trustable is one of the most important capabilities of H1st objects, most notably, of H1st Models. It really comprises each of the capabilities below.

Auditable
#########
To be trusted, an object (Model) must be Auditable. It means that the object self-records an audit trail of its provenance and decisions, so that authorized personnel can query the object with questions like, “When was this model trained? Who did it? What was the data it was trained with? What biases exist in that training data? What is the history of decisions made by this model and what were the corresponding input data?”

Describable
###########
To be trusted, an object (Model) must at minimum be Describable. It means that the object is self-describing when queried, with information such as “What the intent of the model is, and how it is designed to achieve that intent?”

Explainable
###########
To be trusted, an object (Model) must also be Explainable. It means that authorized personnel can query the object with questions like, “What are the top 3 most important input features for this model? Why did this model make that particular decision in that way?”

Debiasable
##########
To be trusted, an object (Model) must further be Debiasable. It is an inescapable rule that all Models are biased, because all data samples are biased. The only question is whether the axis of those biases are protected characteristics, and what is the impact of those biases. If an undesirable impact is likely to be felt, a Debiasable Model must allow itself to correct its output, so as to remove or mitigate that impact. Furthermore, a Debiasable Model may allow its output to be adjusted so as to model the world as it should be, rather than the world as it is in the data.

Constituency
############
It’s important to differentiate an Explanation made to a Consumer vs. one made to a Regulator. Each Constituency has different interests and must be treated differently.

  - DATA_SCIENTIST
  - BUSINESS_MANAGER
  - CUSTOMER
  - USER
  - CONSUMER
  - REGULATOR
  - LEGISLATOR
  - ANY OTHER

Aspect
######
Each given question asked of a Model belongs to a different Aspect of that Model.

  - ACCOUNTABLE
  - FUNCTIONAL
  - OPERATIONAL
  - ANY OTHER
