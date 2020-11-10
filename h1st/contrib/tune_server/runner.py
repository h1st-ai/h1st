import sys
import json
import os
import importlib
import multiprocessing
import traceback
import datetime
from typing import List, Optional

import ulid
import psutil
from pydantic import BaseModel

import h1st
from h1st.model_repository import ModelRepository
from h1st.tuner import HyperParameterTuner


class TuneConfig(BaseModel):
    id: str = ""
    working_dir: str = ""
    model_class: str = ""
    parameters: list = []
    options: dict = {}
    target_metric: str = ""


class TuneRun(BaseModel):
    id: str = ""
    model_class: str = ""
    config: TuneConfig = None
    best_result: dict = {}
    status: str = ""
    error: str = ""
    traceback: str = ""
    created_at: datetime.datetime = None
    finished_at: datetime.datetime = None


class TuneRunner:
    def __init__(self):
        pass

    def run(self, config: TuneConfig):
        storage = self.storage
        run_id = str(ulid.new())
        tune_namespace = f"tune::runs::{run_id}::"

        # remember default value
        # storage.set_obj(f"tune::runs::default::config", config.dict())

        config.id = run_id

        storage.set_obj(tune_namespace + "config", config.dict())

        process = multiprocessing.Process(target=_run, args=[
            config.dict(),
            tune_namespace,
        ])

        try:
            storage.set_obj(tune_namespace + "status", {
                "status": "running",
                "model_class": config.model_class,
            })

            process.daemon = True
            process.start()

            storage.set_obj(tune_namespace + "pid", process.pid)

            return run_id, process.pid
        except Exception as ex:
            if process:
                process.terminate()

            storage.set_obj(tune_namespace + "status", {
                "status": "error",
                "model_class": config.model_class,
                "error": str(ex),
                "traceback": traceback.format_exc(),
            }) 

    def list_runs(self, offset=None, limit=None) -> List[TuneRun]:
        """
        Return runs by order descending time order
        """
        storage = self.storage
        tune_namespace = "tune::runs"

        keys = storage.list_keys(tune_namespace)[::-1]

        if offset is not None:
            keys = keys[offset:]

        if limit is not None:
            keys = keys[:limit]

        result = []
        for k in keys:
            run = self.get_run(k)
            result.append(run)

        return result

    def get_default_config(self, model_class) -> TuneConfig:
        try:
            tune_namespace = f"tune::default::{model_class}"
            result = self.storage.get(tune_namespace)
            result = TuneConfig(**result)
        except KeyError:
            result = None

        return result

    def get_run(self, run_id, detail=False) -> TuneRun:
        storage = self.storage
        tune_namespace = f"tune::runs::{run_id}::"

        run = TuneRun(
            id=run_id,
            created_at=ulid.parse(run_id).timestamp().datetime,
        )

        if detail:
            run.config = storage.get_obj(f"{tune_namespace}config")

        status = storage.get_obj(f"{tune_namespace}status")
        run.status = status['status']
        run.model_class = status.get('model_class')
        run.error = status.get('error')
        run.traceback = status.get('traceback')
        run.finished_at = status.get('finished_at')
        run.best_result = status.get('best_result')

        return run

    def get_analysis_result(self, run_id):
        storage = self.storage
        tune_namespace = f"tune::runs::{run_id}::"
        return storage.get_obj(tune_namespace + "result")

    def wait(self, run_id):
        storage = self.storage
        tune_namespace = f"tune::runs::{run_id}::"

        pid = storage.get_obj(tune_namespace + "pid")
        process = psutil.Process(pid)
        while True:
            try:
                process.wait(1)
                break
            except psutil.TimeoutExpired:
                continue

    @property
    def storage(self):
        return ModelRepository.get_model_repo()._storage


def _run(config_dict, tune_namespace):
    """
    Actual run function
    """
    # XXX
    storage = ModelRepository.get_model_repo()._storage

    try:
        config = TuneConfig(**config_dict)

        if config.working_dir:
            os.chdir(config.working_dir)

        h1st.init()

        bits = config.model_class.split(".")
        class_name = bits.pop()
        module_name = ".".join(bits)
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)

        tuner = HyperParameterTuner()
        analysis = tuner.run(model_class, config.parameters, config.target_metric, config.options)

        records = analysis.to_dict('records')

        storage.set_obj(tune_namespace + "result", records)
        storage.set_obj(tune_namespace + "status", {
            "status": "success",
            "model_class": config.model_class,
            "finished_at": datetime.datetime.now(),
            "best_result": records[0],
        })
    except Exception as ex:
        storage.set_obj(tune_namespace + "status", {
            "status": "error",
            "model_class": config.model_class,
            "error": str(ex),
            "traceback": traceback.format_exc(),
            "finished_at": datetime.datetime.now(),
        })


if __name__ == "__main__":
    config_file = sys.argv[1]

    with open(config_file, "r") as f:
        tune_config = TuneConfig(**json.load(f))

    runner = TuneRunner()

    run_id, _ = runner.run(tune_config)
    print(run_id)
    runner.wait(run_id)
