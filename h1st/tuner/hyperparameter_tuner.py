import json
import os    

from filelock import FileLock 
from ray import tune
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.suggest import ConcurrencyLimiter
from ray.tune.suggest.bayesopt import BayesOptSearch

class HyperParameterTuner:
    def run(self, model_class, param_values, metric, options, search_algorithm="BO", scheduler="Async_HB"):
        hyperparameter = getattr(
            model_class, 'hyperparameter', {})['tuning_param']
        target_metrics = getattr(
            model_class, 'hyperparameter', {})['target_metrics']
        # 'tuning_param': {'lr': float, 'units': int}
        # 'target_metrics': {'accuracy': 'minimize'}
        # 'param_values': {'lr': {'min': 0.001, 'max': 0.1},
        #                  'units': [4, 8, 16, 32, 64]}

        h1st_model_trainable = self.create_h1st_model_trainable(model_class, hyperparameter)    
        space = self.get_config_space(param_values, hyperparameter)
        algo = self.get_search_algorithm(search_algorithm)
        scheduler = self.get_scheduler(scheduler)
        metric_mode = self.get_metric_n_mode(target_metrics, metric)

        analysis= tune.run(
            h1st_model_trainable,
            config=space,
            metric=metric_mode[0],
            mode=metric_mode[1],
            search_alg=algo,
            scheduler=scheduler,
            stop={"training_iteration": 5},
            verbose=1,
            num_samples=options['num_samples'],
            # name="my_exp",
        )
        stats = analysis.stats()
        secs = stats["timestamp"] - stats["start_time"]
        print(f'took {secs:7.2f} seconds ({secs/60.0:7.2f} minutes)')

        return analysis

    def get_metric_n_mode(self, target_metrics, metric):
        metric_mode = (None, None)
        if metric == "accuracy":
            metric_mode = ("mean_accuracy", "max")
        elif metric == "loss":
            metric_mode = ("mean_loss", "min")
        else:
            raise Exception(metric, "is a not supported metric")
        return metric_mode

    def get_scheduler(self, scheduler):
        scheduler = AsyncHyperBandScheduler()
        return scheduler

    def get_search_algorithm(self, search_algorithm):
        algo = BayesOptSearch(   
            utility_kwargs={
            "kind": "ucb",
            "kappa": 2.5,
            "xi": 0.0
        })
        algo = ConcurrencyLimiter(algo, max_concurrent=10)
        return algo

    def get_config_space(self, param_values, hyperparameter):
        space = {
            "lr": tune.uniform(0.005, 0.05),
            "units": tune.uniform(1, 64),
            # "epochs": tune.uniform(4, 50),    
            "n_layer": tune.quniform(1, 8, 1.0),    
        #     "units": tune.randint(1, 64),
        #     "n_layer": tune.randint(1, 8)            
        }
        return space

    def create_h1st_model_trainable(self, model_class, hyperparameter):
        class H1stModelTrainable(tune.Trainable):    
            def setup(self, config):
                self.config = config
                self.hyperparameter = hyperparameter
                self.timestep = 0
                self.kwargs = {}
                for k, v in self.hyperparameter.items():
                    self.kwargs[k] = v(round(self.config[k]) if v == int else self.config[k])
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

        return H1stModelTrainable



# class HyperParameterTuner:
#     def run(self, model_class, param_values, metric, search_algorithm="BO", scheduler="Async_HB"):
#         hyperparameter = getattr(
#             model_class, 'hyperparameter', {})['tuning_param']
#         target_metrics = getattr(
#             model_class, 'hyperparameter', {})['target_metrics']
#         # 'tuning_param': {'lr': float, 'units': int}
#         # 'target_metrics': {'accuracy': 'minimize'}
#         # 'param_values': {'lr': {'min': 0.001, 'max': 0.1},
#         #                  'units': [4, 8, 16, 32, 64]}

#         h1st_model_trainable = self.create_h1st_model_trainable(model_class, hyperparameter)    
#         space = self.get_config_space(param_values, hyperparameter)
#         algo = self.get_search_algorithm(search_algorithm)
#         scheduler = self.get_scheduler(scheduler)
#         metric_mode = self.get_metric_n_mode(target_metrics, metric)

#         analysis= tune.run(
#             h1st_model_trainable,
#             config=space,
#             metric=metric_mode[0],
#             mode=metric_mode[1],
#             search_alg=algo,
#             scheduler=scheduler,
#             stop={"training_iteration": 5},
#             verbose=1,
#             num_samples=200,
#             # name="my_exp",
#         )

#     def get_metric_n_mode(self, target_metrics, metric):
#         metric_mode = (None, None)
#         if metric == "accuracy":
#             metric_mode[0] = "mean_accuracy"
#             metric_mode[1] = "max"
#         elif metric == "loss":
#             metric_mode[0] = "mean_loss"
#             metric_mode[1] = "min"
#         else:
#             raise Exception(metric, "is a not supported metric")
#         return metric_mode

#     def get_scheduler(self, scheduler):
#         scheduler = AsyncHyperBandScheduler()
#         return scheduler

#     def get_search_algorithm(self, search_algorithm):
#         algo = BayesOptSearch(   
#             utility_kwargs={
#             "kind": "ucb",
#             "kappa": 2.5,
#             "xi": 0.0
#         })
#         algo = ConcurrencyLimiter(algo, max_concurrent=10)
#         return algo

#     def get_config_space(self, param_values, ):
#         space = {
#             "lr": tune.uniform(0.005, 0.05),
#             "units": tune.uniform(1, 64),
#             "epochs": tune.uniform(4, 50),    
#         #     "units": tune.randint(1, 64),
#         #     "n_layer": tune.randint(1, 8)
#             "n_layer": tune.quniform(1, 8, 1.0),    
#         }
#         return space


#     def create_h1st_model_trainable(self, model_class, hyperparameter):
#         class H1stModelTrainable(tune.Trainable):    
#             def setup(self, config):
#                 self.config = config
#                 self.hyperparameter = hyperparameter
#                 self.timestep = 0
#                 self.kwargs = {}
                
#                 for k, v in self.hyperparameter.items():
#                     self.kwargs[k] = v(self.config[k])
#                 self.h1_ml_model = model_class(**self.kwargs)

#                 DATA_ROOT = './data/credit_card'
#                 lock_file = f'{DATA_ROOT}/data.lock'
#                 if not os.path.exists(DATA_ROOT):
#                     os.makedirs(DATA_ROOT)
#                 with FileLock(os.path.expanduser(lock_file)):
#                     data = self.h1_ml_model.load_data()
#                 self.prepared_data = self.h1_ml_model.prep(data)  
                
#             def step(self):
#                 self.timestep += 1
#                 self.h1_ml_model.train(self.prepared_data)
#                 self.h1_ml_model.evaluate(self.prepared_data)
#                 acc = self.h1_ml_model.metrics['accuracy']
#                 self.h1_ml_model.persist(str(self.timestep) + str())
#                 return {"mean_accuracy": acc}

#             def save_checkpoint(self, checkpoint_dir):
#                 path = os.path.join(checkpoint_dir, "checkpoint")
#                 with open(path, "w") as f:
#                     f.write(json.dumps({"timestep": self.timestep}))
#                 return path

#             def load_checkpoint(self, checkpoint_path):
#                 with open(checkpoint_path) as f:
#                     self.timestep = json.loads(f.read())["timestep"]

#         return H1stModelTrainable        