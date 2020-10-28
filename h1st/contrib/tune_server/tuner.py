import sys
import json
import os
import importlib

import ray
import h1st

from h1st.tuner import HyperParameterTuner
from pydantic import BaseModel



class TuneConfig(BaseModel):
    working_dir: str = ""
    model_class: str = ""
    parameters: list = []
    options: dict = {}
    target_metric: str = ""


def run(config: TuneConfig):
    try:
        return _run(config)
    except:
        # TODO: log exception
        raise

def _run(config: TuneConfig):
    if config.working_dir:
        os.chdir(config.working_dir)

    h1st.init()
    module_name, class_name = config.model_class.split(":", 1)
    module = importlib.import_module(module_name)
    model_class = getattr(module, class_name)

    # TODO: validation

    tuner = HyperParameterTuner()
    result = tuner.run(model_class, config.parameters, config.target_metric, config.options)


if __name__ == "__main__":
    config_file = sys.argv[1]

    with open(config_file, "r") as f:
        config = TuneConfig(**json.load(f))

    print(config.dict())

    run(config)
