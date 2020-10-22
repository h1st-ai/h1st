class Profile:
    """
    A Profile explores bias in a dataset w.r.t. a protected_attribute (e.g. race, gender,
    disability). It stratifies the data into the classes found under the protected_attribute
    feature. It then identifies differences between the strata and their output distributions.
    TODO: If given a specific protected_class, it will stratify the data into two sets, protected
    and non-protected.
    """

    def __init__(self, data, target, protected_attribute):
        # make protected_attributes a list
        # save a dictionary of dictionaries
        """
        Parameters:
            data: DataFrame with features as column names.
            target: Array of labels of the dataset.
            protected_attribute: The feature of the data
            that is to be protected from discrimination. This column is assumed to be categorical.
        """
        self.data = data
        self.target = target
        self.protected_attribute = protected_attribute

        # Returns a dict.
        # Keys are the category within the protected attribute
        # Values are the corresponding subsets of the data WITHOUT the protected attribute column
        self.stratified_data = {}
        self.stratified_target = {}
        categories = set(self.data[self.protected_attribute])
        for category in categories:
            index_vector = (self.data[self.protected_attribute] == category)
            self.stratified_data[category] = self.data[index_vector]
            self.stratified_target[category] = self.target[index_vector]
        for key in self.stratified_data:
            self.stratified_data[key] = self.stratified_data[key].drop(protected_attribute, axis=1)

    def profile(self):
        """
        Compare strata against each other.
        """
        # compare sets with: basic statistics (box plots), relative frequency histograms
        # LATER: for each category within a protected class), (aif360 visuals)
        # if label class is not given, highlight the strongest differences/correlations
