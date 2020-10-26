from flask_migrate import Migrate, upgrade
from fhe_collector import create_app, db
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)
