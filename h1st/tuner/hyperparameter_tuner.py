from datetime import datetime
import json
import os    

import h1st

import ConfigSpace as CS
from filelock import FileLock
from ray import tune
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.schedulers.hb_bohb import HyperBandForBOHB
from ray.tune.suggest import ConcurrencyLimiter
from ray.tune.suggest.bayesopt import BayesOptSearch
from ray.tune.suggest.bohb import TuneBOHB

class HyperParameterTuner:
    def run(
        self,
        model_class,
        parameters,
        target_metrics,
        options,
        search_algorithm="BOHB",
        name="experiment_1"):

        h1st_model_trainable = self.create_h1st_model_trainable(model_class, parameters)
        config_space = self.get_config_space(parameters, search_algorithm)
        metric_mode = self.get_metric_n_mode(target_metrics)
        algo, scheduler = self.get_search_algorithm(
            search_algorithm, config_space, metric_mode, options.get('max_concurrent', 4))

        analysis = tune.run(
            h1st_model_trainable,
            config=config_space if search_algorithm == "BO" else None,
            metric=metric_mode[0],
            mode=metric_mode[1],
            search_alg=algo,
            scheduler=scheduler,
            stop=options.get('stopping_criteria', {'training_iteration': 5}),
            verbose=1,
            num_samples=options.get('num_samples', 20),
            name=name,
        )
        stats = analysis.stats()
        secs = stats["timestamp"] - stats["start_time"]
        print(f"took {secs:7.2f} seconds ({secs/3600.0:3.0f} hours {(secs/60.0)%60:2.2f} minutes)")

        cols = ['model_version', metric_mode[0], 'training_iteration'] \
               + [f'config/{param["name"]}' for param in parameters]
        analysis = analysis.dataframe()[cols].sort_values(
            metric_mode[0], ascending=False if metric_mode[1]=='max' else True)
        return analysis

    def get_metric_n_mode(self, target_metrics):
        metric_mode = (None, None)
        if target_metrics == "accuracy":
            metric_mode = ("mean_accuracy", "max")
        elif target_metrics == "loss":
            metric_mode = ("mean_loss", "min")
        else:
            raise Exception(target_metrics, "is not a supported metric")
        return metric_mode

    # def get_scheduler(self, scheduler):
    #     scheduler = AsyncHyperBandScheduler()
    #     return scheduler

    def get_search_algorithm(
        self, search_algorithm, config_space, metric_mode, max_concurrent):
        if search_algorithm == "BO":
            algo = BayesOptSearch(   
                utility_kwargs={
                "kind": "ucb",
                "kappa": 2.5,
                "xi": 0.0
            })
            algo = ConcurrencyLimiter(algo, max_concurrent=max_concurrent)
            scheduler = AsyncHyperBandScheduler()
        elif search_algorithm == "BOHB":
            experiment_metrics = dict(metric=metric_mode[0], mode=metric_mode[1])
            algo = TuneBOHB(
                config_space, max_concurrent=max_concurrent, **experiment_metrics)
            scheduler = HyperBandForBOHB(
                time_attr="training_iteration",
                reduction_factor=4)
        else:
            raise Exception(search_algorithm, "is not available yet")
        return algo, scheduler

    def get_config_space(self, parameters, search_algorithm):
        if search_algorithm == "BO":
            config_space = self.get_config_space_bo(parameters)
        elif search_algorithm == "BOHB":
            config_space = self.get_config_space_bohb(parameters)
        else:
            raise Exception(search_algorithm, "is not available yet")            
        return config_space

    def get_config_space_bo(self, parameters):
        config_space = {}
        for param in parameters:
            name_ = param.get('name')
            min_ = param.get('min')
            max_ = param.get('max')
            choice_ = param.get('choice', [])            
            if (min_ is not None) and (max_ is not None):
                config_space[name_] = tune.uniform(min_, max_)
            elif len(choice_) != 0:
                raise Exception("bayesian optimization doesn't support categorical input in", name_)
            else:
                raise Exception("value of", param, "was not provided")
        return config_space

    def get_config_space_bohb(self, parameters):
        config_space = CS.ConfigurationSpace()
        for param in parameters:
            name_ = param.get('name')
            type_ = param.get('type')
            min_ = param.get('min')
            max_ = param.get('max')
            choice_ = param.get('choice', [])
            if (min_ is not None) and (type_ == "float"):
                config_space.add_hyperparameter(
                    CS.UniformFloatHyperparameter(
                        name_, lower=min_, upper=max_))
            elif (min_ is not None) and (type_ == "int"):
                config_space.add_hyperparameter(
                    CS.UniformIntegerHyperparameter(
                        name_, lower=min_, upper=max_))
            elif len(choice_) != 0:
                config_space.add_hyperparameter(
                    CS.CategoricalHyperparameter(name_, choices=choice_))
            else:
                raise Exception("value of", name_, "was not provided.")
        return config_space

    def create_h1st_model_trainable(self, model_class, parameters):
        class H1stModelTrainable(tune.Trainable):
            def setup(self, config):
                h1st.init()

                self.config = config
                self.hyperparameter = parameters
                self.timestep = 0
                self.kwargs = {}

                for param in self.hyperparameter:
                    k = param["name"]
                    # print(self.config[k])

                    # self.kwargs[k] = param["type"](round(self.config[k]) if param["type"] == "int" else self.config[k])
                    self.kwargs[k] = int(round(self.config[k])) if param["type"]=="int" \
                                        else float(self.config[k]) if param["type"]=="float" \
                                        else self.config[k]
                    
                # for k, v in self.hyperparameter.items():
                #     self.kwargs[k] = v(round(self.config[k]) if v == int else self.config[k])
                self.h1_ml_model = model_class(**self.kwargs)

                DATA_LOCK_DIR = "./data_lock"
                lock_file = f"{DATA_LOCK_DIR}/data.lock"
                if not os.path.exists(DATA_LOCK_DIR):
                    os.makedirs(DATA_LOCK_DIR)
                with FileLock(os.path.expanduser(lock_file)):
                    data = self.h1_ml_model.load_data()
                self.prepared_data = self.h1_ml_model.prep(data)

            def step(self):
                self.timestep += 1
                self.h1_ml_model.train(self.prepared_data)
                self.h1_ml_model.evaluate(self.prepared_data)
                acc = self.h1_ml_model.metrics["accuracy"]
                model_version = f'{"|".join([f"{k[:3]}={v}" for k, v in self.kwargs.items()])}|{self.timestep}{datetime.now().strftime("%S%f")}'
                self.h1_ml_model.persist(model_version)
                return {"mean_accuracy": acc, "model_version": model_version}

            def save_checkpoint(self, checkpoint_dir):
                path = os.path.join(checkpoint_dir, "checkpoint")
                with open(path, "w") as f:
                    f.write(json.dumps({"timestep": self.timestep}))
                return path

            def load_checkpoint(self, checkpoint_path):
                with open(checkpoint_path) as f:
                    self.timestep = json.loads(f.read())["timestep"]

        return H1stModelTrainable


"""
[Old version]
Get parameters and targets from model class and run method. 
"""

# class HyperParameterTuner:
#     def run(self, model_class, param_values, metric, options, search_algorithm="BO", scheduler="Async_HB"):
#         hyperparameter = getattr(
#             model_class, "hyperparameter", {})["tuning_param"]
#         target_metrics = getattr(
#             model_class, "hyperparameter", {})["target_metrics"]
#         # "tuning_param": {"lr": float, "units": int}
#         # "target_metrics": {"accuracy": "minimize"}
#         # "param_values": {"lr": {"min": 0.001, "max": 0.1},
#         #                  "units": [4, 8, 16, 32, 64]}

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
#             num_samples=options["num_samples"],
#             # name="my_exp",
#         )
#         stats = analysis.stats()
#         secs = stats["timestamp"] - stats["start_time"]
#         print(f"took {secs:7.2f} seconds ({secs/60.0:7.2f} minutes)")

#         return analysis

#     def get_metric_n_mode(self, target_metrics, metric):
#         metric_mode = (None, None)
#         if metric == "accuracy":
#             metric_mode = ("mean_accuracy", "max")
#         elif metric == "loss":
#             metric_mode = ("mean_loss", "min")
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

#     def get_config_space(self, param_values, hyperparameter):
#         space = {
#             "lr": tune.uniform(0.005, 0.05),
#             "units": tune.uniform(1, 64),
#             # "epochs": tune.uniform(4, 50),    
#             "n_layer": tune.quniform(1, 8, 1.0),    
#         #     "units": tune.randint(1, 64),
#         #     "n_layer": tune.randint(1, 8)            
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
#                     self.kwargs[k] = v(round(self.config[k]) if v == int else self.config[k])
#                 self.h1_ml_model = model_class(**self.kwargs)

#                 DATA_ROOT = "./data/credit_card"
#                 lock_file = f"{DATA_ROOT}/data.lock"
#                 if not os.path.exists(DATA_ROOT):
#                     os.makedirs(DATA_ROOT)
#                 with FileLock(os.path.expanduser(lock_file)):
#                     data = self.h1_ml_model.load_data()
#                 self.prepared_data = self.h1_ml_model.prep(data)  
                
#             def step(self):
#                 self.timestep += 1
#                 self.h1_ml_model.train(self.prepared_data)
#                 self.h1_ml_model.evaluate(self.prepared_data)
#                 acc = self.h1_ml_model.metrics["accuracy"]
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
