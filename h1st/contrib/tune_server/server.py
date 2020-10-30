import os

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
        "result": tuner.get_analysis_result(model_class, run_id),
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
