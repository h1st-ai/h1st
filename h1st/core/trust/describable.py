from .shap_model_describer import SHAPModelDescriber
from .enums import Constituency, Aspect

class Describable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Describable, i.e., they can self-describe their properties and behaviors. For example,
    a `Describable` `Model` should be able to report the data that was used to train it, provide an
    importance-ranked list of its input features on a global basis, etc.
    """

    @property
    def description(self):
        return getattr(self, "__description", {})
    
    @description.setter
    def description(self, value):
        setattr(self, "__description", value)

    def describe(self, constituency=Constituency.ANY, apect=Aspect.ANY):
        '''
        Returns a description of the model's behavior and properties based on `Who's asking` for `what`.

            Parameters:
                constituent : Constituency: The Constituency asking for the explanation `Who`
                aspect : The Aspect of the question. `What`

            Returns:
                out : Description of Model's behavior and properties (SHAP)               
        '''
        ## TODO: For each pair of constituent and aspect write functions to show relevant information.
        print("Description type: {}"\
            .format(h1.Model.Aspect.ACCOUNTABLE.name))
        print("Targeted Constituent: {}"\
            .format(h1.Model.Constituency.DATA_SCIENTIST.name))
        print("Model Metrics : {}".format(self.metrics))
        
        print("Size of the dataset: {}".format(self.data.shape[0]))
        print("Number of features of the dataset: {}".format(len(self.features)))

        if self.shap:
            print("Overview of the features that are most important for the WineQualityModel. Seen in the plot are SHAP values of every feature for every sample.The plot below sorts features by the sum of SHAP value magnitudes over all samples, and uses SHAP values to show the distribution of the impacts each feature has on the model output. The color represents the feature value (red high, blue low). This reveals for example that a high alcohol increases the predicted wine quality.".format())
            d = SHAPModelDescriber(self.model, self.prepared_data, self.plot)      
            return {'shap_values':d.shap_values}
