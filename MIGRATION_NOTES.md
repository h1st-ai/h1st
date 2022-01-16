# MIGRATION NOTES
## From version 2021.06 to version 0.0.3
Due to changes to the package structure, please update your H1st code to:
- Import `Graph` class from `h1st.h1flow.h1flow` module instead of `h1st.core.graph`.
- Import `Node` class and its sub-classes (`Action`, `NoOp`, `Decision`) from `h1st.h1flow.h1step` module instead of `h1st.core.node`.
- Import `NodeContainable` class from `h1st.h1flow.h1step_containable` module instead of `h1st.core.node_containable`.
- Import `Model`, `MLModel`, `RuleBasedModel`, `FuzzyLogicModel` classes from `h1st.model.model`, `h1st.model.ml_model`, `h1st.model.rule_based_model` modules correspondingly instead of `h1st.core.model`.
## From version 0.0.3 to version 0.0.8
- The `Modeler` class is introduced with `build_model` method which is used to build the corresponding `Model` instance. The `Model` class' `load_data`, `explore`, `evaluate` now belongs to the `Modeler` class with `explore` being renamed to `explore_data` and `evaluate` being renamed to `evaluate_model`.
- The `Model` class' `predict` method is renamed to `process`. Its `PredictiveModel` subclass which is then inherited by `RuleBasedModel`, `MLModel` still possess the `predict` method which basically calls the `process` one.
- The `Model` class' `load` is renamed to `load_params`.
## From version 0.8.0 to version 0.1.1
- The `MLModel` class' `train_model` is renamed to `train_base_model` for the purpose of training the base/native ML models.

