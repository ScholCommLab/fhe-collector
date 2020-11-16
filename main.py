from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade
import os
import click

from app.main import create_app
from app.models import Url, Doi, FBRequest
from app.db import init_db, drop_db


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Doi": Doi, "Url": Url, "FBRequest": FBRequest}
