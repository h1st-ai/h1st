import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

class Profiler:
    """
    A Profile explores bias in a dataset w.r.t. a protected_attribute (e.g. race, gender,
    disability). It stratifies the data into the classes found under the protected_attribute
    feature. It then identifies differences between the strata and their output distributions. TODO:
    If given a specific protected_class, it will stratify the data into two sets, protected and
    non-protected.
    """

    def __init__(self, data, target, protected_attributes: list):
        """
        Parameters:
            data: DataFrame with features as column names, includes target array.
            target: Label of the target feature.
            protected_attribute: The feature of the data that is to be protected from
            discrimination. This column is assumed to be categorical.
        Saved dicts:
            Outer keys: protected attributes
            Inner keys: categories within that attribute
                strata: subsetted dataframe or subsetted vector
                summary: dataframe of summary statistics per strata per feature
        """
        self.data = data
        self.target = target
        self.protected_attributes = protected_attributes
        self.strata = {}
        self.summary = {}
        for attribute in self.protected_attributes:
            self.summary[attribute] = {}
            self.strata[attribute] = {}
            categories = set(data[attribute])
            for category in categories:
                index_vector = (data[attribute] == category)
                data_subset = data[index_vector].drop(attribute, axis=1)
                self.strata[attribute][category] = data_subset
                self.summary[attribute][category] = data_subset.describe()

    def profile(self):
        """
        Compare strata against each other and view summary statistics.
        """
        # strata summaries

        # plots
        for attribute in self.protected_attributes:
            # really should make this look prettier, but here's the gist.
            print("*** DATA PROFILE FOR PROTECTED ATTRIBUTE: ", attribute, " ***")
            
            plt.figure(clear=True)
            box = sns.boxplot(data=self.data, x=attribute, y=self.target)
            plt.suptitle("BOX PLOT")
            plt.title("Quartile distributions of " + self.target + " by " + attribute)
            
            plt.figure(clear=True)
            hist = sns.histplot(data=self.data, hue=attribute, x=self.target)
            plt.suptitle("HISTOGRAM")
            plt.title("Frequency distribution of " + self.target + " by " + attribute)
            
            pairs = sns.pairplot(data=self.data.drop(self.target, axis=1), hue=attribute, diag_kind="hist")
            pairs.fig.suptitle("PAIRWISE PLOTS")
        # compare sets with: basic statistics (box plots), relative frequency histograms
        # LATER: for each category within a protected class), (aif360 visuals)
        # if label class is not given, highlight the strongest differences/correlations
