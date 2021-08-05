"""
Schema Inferrer and Validator Module

This module allows you to use schema to define data contract between nodes of the graph.

Schema Definition
-----------------

Schema is defined using python dictionary and python type. Python dictionary is choosen it is easy
to define, easy to read and also easy to extend to add additional meta in the future.

Below are some examples:

.. code-block:: python

    # pandas dataframe with three columns
    my_df_schema = {
        "type": pd.DataFrame,
        "fields": {
            "feature1": float,
            "feature2": float,
            "label": str,
        }
    }

    # numpy array schema with shape
    my_np_schema = {
        "type": np.ndarray,
        "item": float,
        "shape": (None, 24, 24),
    }

    # list of integer
    my_list_schema = {
        "type": list,
        "item": int
    }


Schema Validation
-----------------

You can use the ``SchemaValidator`` to validate the schema as following

.. code-block:: python

    my_schema = {'type': list, 'item': int}
    validator = SchemaValidator()
    result = validator.validate(my_schema, [1, 2, 3])

    # print the validation result to console
    result.display()


"""


from h1st.unused.schema.schema_inferrer import SchemaInferrer
from h1st.unused.schema.schema_validation_result import SchemaValidationResult
from h1st.unused.schema.schema_validator import SchemaValidator
