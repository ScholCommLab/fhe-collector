# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/ScholCommLab/fhe-collector.

Copyright 2018 Stefan Kasberger

Licensed under the MIT License.
"""
import click
import os
from flask import Flask
from flask.cli import with_appcontext
from flask_migrate import Migrate
from app.bp.api import blueprint as api_blueprint
from app.bp.api.v1 import blueprint as api_v1_blueprint
from app.bp.main import blueprint as main_blueprint
from app.bp.main.errors import not_found_error, internal_error
from app.config import get_config_class
from app.db import (
    close_db,
    create_doi_lp_urls,
    create_doi_new_urls,
    create_doi_old_urls,
    create_ncbi_urls,
    create_unpaywall_urls,
    dev,
    drop_db,
    get_fb_data,
    get_config,
    import_basedata,
    init_db,
)
from app.models import db


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
migrate = Migrate()


def create_app() -> Flask:
    """Create application and load settings."""
    print("* Start FHE Collector...")

    config = get_config_class(os.getenv("FLASK_CONFIG"))
    app = Flask("fhe_collector", root_path=ROOT_DIR)
    app.config.from_object(config())
    config.init_app(app)

    init_app(app)
    db.init_app(app)

    migrate.init_app(app, db)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(api_v1_blueprint, url_prefix="/api/v1")

    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    print(' * Settings "{0}" loaded'.format(os.getenv("FLASK_CONFIG")))
    print(" * Environment: " + app.config["FLASK_ENV"])
    print(" * Database: " + app.config["SQLALCHEMY_DATABASE_URI"])

    return app


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)
    app.cli.add_command(deploy_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(import_basedata_command)
    app.cli.add_command(doi_new_command)
    app.cli.add_command(doi_old_command)
    app.cli.add_command(doi_lp_command)
    app.cli.add_command(ncbi_command)
    app.cli.add_command(unpaywall_command)
    app.cli.add_command(fb_command)
    app.cli.add_command(dev_command)


@click.command("dev")
@with_appcontext
def dev_command() -> None:
    dev()
    click.echo("dev finished.")


@click.command("initdb")
@with_appcontext
def init_db_command() -> None:
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Database initialized.")


@click.command("dropdb")
@with_appcontext
def drop_db_command() -> None:
    """Clear existing data and create new tables."""
    drop_db()
    click.echo("Database dropped.")


@click.command("deploy")
@with_appcontext
def deploy_command() -> None:
    """Run deployment tasks."""
    click.echo("App deployed.")


@click.command("resetdb")
@with_appcontext
def reset_db_command() -> None:
    """Delete all entries in all tables."""
    drop_db()
    init_db()
    click.echo("Database reseted")


@click.command("import-basedata")
@click.argument("filename")
@click.option("--reset", "-r", is_flag=True, help="Reset database before import.")
@with_appcontext
def import_basedata_command(filename: str, reset: bool) -> None:
    """Delete all entries in all tables."""
    import_basedata(filename, reset)
    click.echo("Basedata imported.")


@click.command("doi-new")
@with_appcontext
def doi_new_command() -> None:
    """Create the new doi URL's."""
    create_doi_new_urls()


@click.command("doi-old")
@with_appcontext
def doi_old_command() -> None:
    """Create the old doi URL's."""
    create_doi_old_urls()


@click.command("doi-lp")
@with_appcontext
def doi_lp_command() -> None:
    """Create the doi landing page URL's."""
    create_doi_lp_urls()


@click.command("ncbi")
@with_appcontext
def ncbi_command() -> None:
    """Create the NCBI URL's."""
    create_ncbi_urls()


@click.command("unpaywall")
@with_appcontext
def unpaywall_command() -> None:
    """Create the Unpaywall URL's."""
    create_unpaywall_urls()


@click.command("fb")
@with_appcontext
def fb_command() -> None:
    """Create the Facebook request."""
    get_fb_data()
