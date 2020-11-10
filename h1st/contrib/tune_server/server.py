import os

from typing import Optional

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings
from h1st.model_repository.explorer import ModelExplorer

from .runner import TuneConfig, TuneRunner

class Settings(BaseSettings):
    project_root: str = os.getcwd()
    allowed_cors_origins: str = ""


settings = Settings()
app = FastAPI()


if settings.allowed_cors_origins:
    origins = settings.allowed_cors_origins.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/api")
def info():
    return settings.dict()


@app.get("/api/models")
def get_models() -> dict:
    explorer = ModelExplorer(settings.project_root)
    models = explorer.discover_models()

    # TODO: fill with last config

    return {
        "items": list(models.values())
    }


@app.get("/api/tune")
def list_tune() -> dict:
    tuner = TuneRunner()
    return {
        "items": [i.dict() for i in tuner.list_runs()]
    }


@app.get("/api/tune/{run_id}")
def get_tune(run_id: str) -> dict:
    tuner = TuneRunner()
    item = tuner.get_run(run_id, True)

    if item.status == "success":
        result = tuner.get_analysis_result(run_id)
    else:
        result = None

    return {
        "item": item,
        "result": result,
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
