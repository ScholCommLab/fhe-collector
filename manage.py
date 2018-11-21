import csv
from flask_script import Manager, Server, Command, prompt_bool
from flask_script.commands import ShowUrls, Clean
from app import create_app
from app.models import db, Publication


app = create_app()
manager = Manager(app)
