import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

class Profile:
    """
    A Profile explores bias in a dataset w.r.t. a protected_attribute (e.g. race, gender,
    disability). It stratifies the data into the classes found under the protected_attribute
    feature. It then identifies differences between the strata and their output distributions.
    TODO: If given a specific protected_class, it will stratify the data into two sets, protected
    and non-protected.
    """

    def __init__(self, data, target, protected_attributes: list):
        """
        Parameters:
            data: DataFrame with features as column names.
            target: Array of labels of the dataset.
            protected_attribute: The feature of the data
            that is to be protected from discrimination. This column is assumed to be categorical.
        """
        self.protected_attributes = protected_attributes
        """
        STRATA INFORMATION
            Outer keys: protected attributes
            Inner keys: categories within that attribute
            STRATA values: subsetted dataframe or subsetted vector
            SUMMARY values: dict of the following
                HISTOGRAM: hist object with sub-histograms per column 
                STATISTICS: DataFrame object with per-column summary statistics
        """
        self.strata = {} # dict of dicts of DATAFRAMES
        self.target = {} # dict of dicts of VECTORS
        self.strata_summary = {} # dict of dicts of DATAFRAMES
        self.target_summary = {} # dict of dicts of one-column DATAFRAMES
        for attribute in self.protected_attributes:
            categories = set(data[attribute])
            for cat in categories:
                index_vector = (data[attribute] == cat)
                data_subset = data[index_vector].drop(attribute, axis=1)
                target_subset = target[index_vector]

                self.strata[attribute][cat] = data_subset
                self.strata_summary[attribute][cat]["statistics"] = data_subset.describe()
                self.strata_summary[attribute][cat]["histogram"] = data_subset.hist()

                self.target[protected_attribute][cat] = target_subset
                self.target_summary[attribute][cat]["statistics"] = target_subset.describe()
                self.target_summary[attribute][cat]["histogram"] = target_subset.hist()

    def profile(self):
        """
        Compare strata against each other.
        """
        # compare sets with: basic statistics (box plots), relative frequency histograms
        # LATER: for each category within a protected class), (aif360 visuals)
        # if label class is not given, highlight the strongest differences/correlations
