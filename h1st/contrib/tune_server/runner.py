import sys
import json
import os
import importlib
import multiprocessing
import traceback
import datetime
from typing import List

import ulid
import ray
import h1st
import psutil

from h1st.model_repository import ModelRepository
from h1st.model_repository.storage import create_storage
from h1st.tuner import HyperParameterTuner
from pydantic import BaseModel


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
        tune_namespace = f"tune::{config.model_class}::{run_id}::"

        config.id = run_id

        storage.set_obj(tune_namespace + "config", config.dict())

        process = multiprocessing.Process(target=_run, args=[
            config.dict(),
            tune_namespace,
        ])

        try:
            process.daemon = True
            process.start()

            storage.set_obj(tune_namespace + "pid", process.pid)

            return run_id, process.pid
        except Exception as ex:
            if process:
                process.terminate()

            storage.set_obj(tune_namespace + "result", {
                "status": "error",
                "error": str(ex),
                "traceback": traceback.format_exc(),
            })

    def list_runs(self, model_class, offset=None, limit=None) -> List[TuneRun]:
        storage = self.storage
        tune_namespace = f"tune::{model_class}"

        keys = storage.list_keys(tune_namespace)

        if offset is not None:
            keys = keys[offset:]

        if limit is not None:
            keys = keys[:limit]

        result = []
        for k in keys:
            run = self.get_run(model_class, k)
            result.append(run)

        return result

    def get_run(self, model_class, run_id, detail=False) -> TuneRun:
        storage = self.storage
        tune_namespace = f"tune::{model_class}::{run_id}::"

        run = TuneRun(
            id=run_id,
            model_class=model_class,
            created_at=ulid.parse(run_id).timestamp().datetime,
        )

        if detail:
            run.config = storage.get_obj(f"{tune_namespace}config")

        try:
            status = storage.get_obj(f"{tune_namespace}result")
            run.status = status['status']
            run.error = status.get('error')
            run.traceback = status.get('traceback')
            run.finished_at = status.get('finished_at')
        except KeyError:
            # TODO: check pid
            run.status = "running"

        return run

    def wait(self, model_class, run_id):
        storage = self.storage
        tune_namespace = f"tune::{model_class}::{run_id}::"

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
        result = tuner.run(model_class, config.parameters, config.target_metric, config.options)

        # TODO: save result

        storage.set_obj(tune_namespace + "result", {
            "status": "success",
            "finished_at": datetime.datetime.now(),
        })
    except Exception as ex:
        storage.set_obj(tune_namespace + "result", {
            "status": "error",
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
    runner.wait(tune_config.model_class, run_id)
