from flask_migrate import Migrate, upgrade
from fhe_collector import create_app, db


app = create_app()
migrate = Migrate(app, db)
