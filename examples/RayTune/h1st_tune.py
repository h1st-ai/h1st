import json
import os    

from filelock import FileLock 
from ray import tune

from examples.RayTune.tensorflow_mlp_classifier import TensorflowMLPClassifier
# kwargs = {
#     'units': int(config['units']),
#     'epochs': int(config['epochs']), 
#     'lr': config['lr'], 
#     'n_layer': int(config['n_layer'])
# }
model_class = TensorflowMLPClassifier

class H1stTunable(tune.Trainable):    
    def setup(self, config):
        self.timestep = 0
#         self.config = config
#         self.timestep = 0
        self.kwargs = {}
        self.hyperparameter = getattr(
            model_class, 'hyperparameter', {})['tuning_param']
        for k, v in self.hyperparameter.items():
            self.kwargs[k] = v(config[k])
        self.h1_ml_model = model_class(**self.kwargs)

        DATA_ROOT = './data/credit_card'
        lock_file = f'{DATA_ROOT}/data.lock'
        if not os.path.exists(DATA_ROOT):
            os.makedirs(DATA_ROOT)
        with FileLock(os.path.expanduser(lock_file)):
            data = self.h1_ml_model.load_data()
        self.prepared_data = self.h1_ml_model.prep(data)  
        
    def step(self):
        self.timestep += 1
        self.h1_ml_model.train(self.prepared_data)
        self.h1_ml_model.evaluate(self.prepared_data)
        acc = self.h1_ml_model.metrics['accuracy']
        self.h1_ml_model.persist(str(self.timestep) + str())
        return {"mean_accuracy": acc}

    def save_checkpoint(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps({"timestep": self.timestep}))
        return path

    def load_checkpoint(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.timestep = json.loads(f.read())["timestep"]

