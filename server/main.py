"""
BVAB Eval API — entrypoint for uvicorn.

Run from this folder:  uvicorn main:app --reload --port 8787
"""
from app.factory import create_app

app = create_app()
