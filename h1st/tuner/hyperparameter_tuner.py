from datetime import datetime
import json
import os
import random

import ConfigSpace as CS
from filelock import FileLock
import ray
from ray import tune
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.schedulers.hb_bohb import HyperBandForBOHB
from ray.tune.suggest import ConcurrencyLimiter
from ray.tune.suggest.bayesopt import BayesOptSearch
from ray.tune.suggest.bohb import TuneBOHB
from ray.tune.schedulers import PopulationBasedTraining

import h1st

class HyperParameterTuner:
    def run(
        self,
        model_class,
        parameters,
        target_metric,
        options,
        search_algorithm="BOHB",
        name="experiment_1",
        verbose=1):

        ray.init(ignore_reinit_error=True)

        h1st_model_trainable = self.create_h1st_model_trainable(model_class, parameters, target_metric)
        config_space, config_space2 = self.get_config_space(parameters, search_algorithm)
        mode = self.get_mode(target_metric)
        algo, scheduler = self.get_search_algorithm(
            # TODO - max_concurrent
            # 1. Default should be the number of cpu
            # 2. cannot be bigger than num_samples
            search_algorithm, config_space, target_metric, mode, options.get('max_concurrent', 4))
        print("search_algorithm:", search_algorithm)
        analysis = tune.run(
            h1st_model_trainable,
            config=config_space2,
            metric=target_metric,
            mode=mode,
            search_alg=algo,
            scheduler=scheduler,
            stop=options.get('stopping_criteria', {'training_iteration': 10}),
            verbose=verbose,
            num_samples=options.get('num_samples', 20),
            name=name,
        )
        ray.shutdown()
        stats = analysis.stats()
        secs = stats["timestamp"] - stats["start_time"]
        print(f"took {secs:7.2f} seconds ({secs/3600.0:3.0f} hours {(secs/60.0)%60:2.2f} minutes)")
        print("best config: ", analysis.get_best_config(metric=target_metric, mode=mode))
        cols = ['model_version', target_metric, 'training_iteration'] \
               + [f'config/{param["name"]}' for param in parameters]
        analysis = analysis.dataframe()[cols].sort_values(
            target_metric, ascending=mode=='min')
        analysis.rename(
            {f'config/{param["name"]}':param["name"] for param in parameters},
            axis='columns',
            inplace=True
        )
        return analysis

    def get_mode(self, target_metric):
        mode = None
        if target_metric == "accuracy":
            mode = "max"
        elif target_metric == "loss":
            mode = "min"
        else:
            raise Exception(target_metric, "is not a supported metric")
        return mode

    # def get_scheduler(self, scheduler):
    #     scheduler = AsyncHyperBandScheduler()
    #     return scheduler

    def get_search_algorithm(
        self, search_algorithm, config_space, metric, mode, max_concurrent):
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
            experiment_metrics = dict(metric=metric, mode=mode)
            algo = TuneBOHB(
                config_space, max_concurrent=max_concurrent, **experiment_metrics)
            scheduler = HyperBandForBOHB(
                time_attr="training_iteration",
                reduction_factor=4)
        elif search_algorithm == "PBT":
            algo = None
            scheduler = PopulationBasedTraining(
                time_attr='training_iteration',
                perturbation_interval=2,  # Every N time_attr units, "perturb" the parameters.
                hyperparam_mutations=config_space)
        else:
            raise Exception(search_algorithm, "is not available yet")
        return algo, scheduler

    def get_config_space(self, parameters, search_algorithm):
        if search_algorithm == "BO":
            config_space = self.get_config_space_bo(parameters)
            config_space2 = config_space
        elif search_algorithm == "BOHB":
            config_space = self.get_config_space_bohb(parameters)
            config_space2 = None
        elif search_algorithm == "PBT":
            config_space = self.get_config_space_pbt(parameters)
            config_space2 = {}
            for param in parameters:
                config_space2[param["name"]] = param["min"] if param["min"] is not None else param["choice"][0]
        else:
            raise Exception(search_algorithm, "is not available yet")            
        return config_space, config_space2

    def get_config_space_pbt(self, parameters):
        config_space = {}
        for param in parameters:
            name_ = param.get('name')
            type_ = param.get('type')
            min_ = param.get('min')
            max_ = param.get('max')
            choice_ = param.get('choice', [])
            if (min_ is not None) and (type_ == "float"):
                config_space[name_] = lambda: random.uniform(min_, max_)
            elif (min_ is not None) and (type_ == "int"):
                config_space[name_] = lambda: random.randint(min_, max_)
            elif len(choice_) != 0:
                config_space[name_] = choice_
            else:
                raise ValueError("value of", name_, "was not provided.")
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
                raise ValueError("bayesian optimization doesn't support categorical input in", name_)
            else:
                raise ValueError("value of", param, "was not provided")
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
                raise ValueError("value of", name_, "was not provided.")
        return config_space

    def create_h1st_model_trainable(self, model_class, parameters, target_metric):
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
                metrics = self.h1_ml_model.metrics[target_metric]
                # model_version = f'{"|".join([f"{k[:3]}={v}" for k, v in self.kwargs.items()])}|{self.timestep}{ datetime.now().strftime("%S%f")}'
                model_version = f'{"|".join([f"{k[:3]}={v}" for k, v in self.kwargs.items()])}|{target_metric[:4]}={metrics:.4f}'
                self.h1_ml_model.persist(model_version)
                return {target_metric: metrics, "model_version": model_version}

            def save_checkpoint(self, checkpoint_dir):
                path = os.path.join(checkpoint_dir, "checkpoint")
                with open(path, "w") as f:
                    f.write(json.dumps({"timestep": self.timestep}))
                return path

            def load_checkpoint(self, checkpoint_path):
                with open(checkpoint_path) as f:
                    self.timestep = json.loads(f.read())["timestep"]

        return H1stModelTrainable
