# USAGE NOTES
## July 16th 2020
Due to changes to the package structure, please update your code to:
- Import `Graph` class from `h1st.h1flow.h1flow` instead `h1st.core.graph` .
- Import `Node` class from `h1st.h1flow.h1step` instead of `h1st.core.node`.
- Import `NodeContainable` from `h1st.h1flow.h1step_containable` instead of `h1st.core.node_containable`.
- Import `Model`, `MLModel`, `RuleBasedModel`, `FuzzyLogicModel` from `h1st.model.model`, `h1st.model.ml_model`, `h1st.model.rule_based_model` instead of `h1st.core.model`.