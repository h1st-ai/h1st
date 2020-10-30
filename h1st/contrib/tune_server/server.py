import os

from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseSettings
from h1st.model_repository.explorer import ModelExplorer

from .runner import TuneConfig, TuneRunner

class Settings(BaseSettings):
    project_root: str = os.getcwd()


settings = Settings()
app = FastAPI()


@app.get("/api")
def info():
    return settings.dict()


@app.get("/api/models")
def get_models() -> dict:
    explorer = ModelExplorer(settings.project_root)
    models = explorer.discover_models()
    return {
        "items": list(models.values())
    }

@app.get("/api/tune")
def list_tune(model_class: str) -> dict:
    if not model_class:
        raise HTTPException(status_code=400)

    tuner = TuneRunner()
    return {
        "items": [i.dict() for i in tuner.list_runs(model_class)]
    }


@app.get("/api/tune/{run_id}")
def get_tune(run_id: str, model_class: str) -> dict:
    if not model_class:
        raise HTTPException(status_code=400)

    tuner = TuneRunner()
    item = tuner.get_run(model_class, run_id, True)
    return {
        "item": item,
        "trials": [],
    }

@app.post('/api/tune/start')
def start_tune(config: TuneConfig) -> dict:
    tuner = TuneRunner()
    run_id, _ = tuner.run(config)
    return {
        "item": {
            "id": run_id,
            "model_class": config.model_class,
        }
    }
