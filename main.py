from app.db import get_db
from app.main import create_app
from app.models import Doi
from app.models import FBRequest
from app.models import Url


app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Open shell."""
    db = get_db()
    return {"db": db, "Doi": Doi, "Url": Url, "FBRequest": FBRequest}
