# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""ORM Models."""
from datetime import datetime
from datetime import timezone

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy.exc import IntegrityError


db = SQLAlchemy()
BaseModelType: DefaultMeta = db.Model


class BaseModel(BaseModelType):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=True)

    def before_save(self, *args, **kwargs):
        pass

    def after_save(self, *args, **kwargs):
        pass

    def save(self, db, commit=True):
        self.before_save()
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
                db.session.refresh(self)
            except Exception as e:
                db.session.rollback()
                raise e

        self.after_save()

    @classmethod
    def before_bulk_create(cls, iterable, *args, **kwargs):
        pass

    @classmethod
    def after_bulk_create(cls, model_objs, *args, **kwargs):
        pass

    @classmethod
    def bulk_create(cls, db, iterable, *args, **kwargs):
        cls.before_bulk_create(iterable, *args, **kwargs)
        model_objs = []
        for data in iterable:
            if not isinstance(data, cls):
                data = cls(**data)
            model_objs.append(data)

        cls.bulk_save_objects(db, model_objs)
        if kwargs.get("commit", True) is True:
            db.session.commit()
        cls.after_bulk_create(model_objs, *args, **kwargs)
        return model_objs

    @classmethod
    def bulk_save_objects(cls, db, model_objs):
        for o in model_objs:
            db.session.add(o)

    @classmethod
    def bulk_create_or_none(cls, db, iterable, *args, **kwargs):
        try:
            return cls.bulk_create(db, iterable, *args, **kwargs)
        except IntegrityError as e:
            db.session.rollback()
            print(e)
            return None

    def before_update(self, *args, **kwargs):
        pass

    def after_update(self, *args, **kwargs):
        pass

    def update(self, db, *args, **kwargs):
        self.before_update(*args, **kwargs)
        db.session.commit()
        self.after_update(*args, **kwargs)

    def delete(self, db, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()


class Import(BaseModel):
    """Imports of basic data done.

    source: '<file FILENAME>', '<uri URI>', 'api'
    """

    __tablename__ = "imports"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String, nullable=False)
    raw = db.Column(db.Text)

    def __repr__(self):
        """Repr."""
        return "<Import {0}>".format(self.id)


class Doi(BaseModel):
    """Doi model.

    Defines the publication data type with it's methods for useage of the Flask
    ORM.

    date comes as YYYY-MM-DD
    """

    __tablename__ = "dois"

    doi = db.Column(db.String, primary_key=True, index=True)
    date_published = db.Column(db.DateTime)
    import_id = db.Column(db.Integer, db.ForeignKey("imports.id"))
    pmc_id = db.Column(db.String)
    pm_id = db.Column(db.String)
    url_doi_new = db.Column(db.Boolean, default=False)
    url_doi_old = db.Column(db.Boolean, default=False)
    url_doi_lp = db.Column(db.Boolean, default=False)
    url_ncbi = db.Column(db.Boolean, default=False)
    url_pm = db.Column(db.Boolean, default=False)
    url_pmc = db.Column(db.Boolean, default=False)
    url_unpaywall = db.Column(db.Boolean, default=False)
    is_valid = db.Column(db.Boolean)

    def __repr__(self):
        """Repr."""
        return "<DOI {0}>".format(self.doi)


class Url(BaseModel):
    """Url model.

    url_type:   'ojs', 'doi_new', 'doi_old', 'doi_landingpage',
                'unpaywall', 'pm', 'pmc'
    """

    __tablename__ = "urls"

    url = db.Column(db.String, primary_key=True, index=True)
    doi = db.Column(db.String, db.ForeignKey("dois.doi"), nullable=False)
    url_type = db.Column(db.String, index=True)

    def __repr__(self):
        """Repr."""
        return "<URL {0}>".format(self.url)


class Request(BaseModel):
    """NCBIRequest model."""

    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String, db.ForeignKey("dois.doi"), nullable=False)
    request_url = db.Column(db.String)
    request_type = db.Column(db.String)
    response_content = db.Column(db.Text)
    response_status = db.Column(db.String)

    def __repr__(self):
        """Repr."""
        return '<API Request "{0}">'.format(self.request_type)


class FBRequest(BaseModel):
    """FBRequest model."""

    __tablename__ = "fbrequests"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, db.ForeignKey("urls.url"), nullable=False)
    response = db.Column(db.Text)
    reactions = db.Column(db.Integer)
    shares = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    plugin_comments = db.Column(db.Integer)

    def __repr__(self):
        """Repr."""
        return "<Facebook Request {0}>".format(self.request)
