import os
from typing import Optional

from pydantic import BaseSettings, BaseModel
from h1st.model_repository.explorer import ModelExplorer
from fastapi import FastAPI


class Settings(BaseSettings):
    project_root: str = os.getcwd()




settings = Settings()
app = FastAPI()


@app.get("/models")
def get_models() -> dict:
    explorer = ModelExplorer(settings.project_root)
    models = explorer.discover_models()
    return {
        "items": list(models.values())
    }
