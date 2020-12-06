from flask_migrate import Migrate, upgrade

from app.main import create_app
from app.models import Url, Doi, FBRequest


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Doi": Doi, "Url": Url, "FBRequest": FBRequest}
