# MIGRATION NOTES
## From version 2021.06 to version 0.0.3
Due to changes to the package structure, please update your H1st code to:
- Import `Graph` class from `h1st.h1flow.h1flow` module instead of `h1st.core.graph`.
- Import `Node` class and its sub-classes (`Action`, `NoOp`, `Decision`) from `h1st.h1flow.h1step` module instead of `h1st.core.node`.
- Import `NodeContainable` class from `h1st.h1flow.h1step_containable` module instead of `h1st.core.node_containable`.
- Import `Model`, `MLModel`, `RuleBasedModel`, `FuzzyLogicModel` classes from `h1st.model.model`, `h1st.model.ml_model`, `h1st.model.rule_based_model` modules correspondingly instead of `h1st.core.model`.