# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""ORM Models."""
from datetime import datetime, timezone, date
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Sequence,
    Date,
    Text,
)
from flask_sqlalchemy import SQLAlchemy


class Base:
    __abstract__ = True

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(Text, nullable=True)

    def before_save(self, *args, **kwargs):
        pass

    def after_save(self, *args, **kwargs):
        pass

    def save(self, db, commit=True):
        self.before_save()
        db.add(self)
        if commit:
            try:
                db.commit()
                db.refresh(self)
            except Exception as e:
                db.rollback()
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
            db.commit()
        cls.after_bulk_create(model_objs, *args, **kwargs)
        return model_objs

    @classmethod
    def bulk_save_objects(cls, db, model_objs):
        for o in model_objs:
            db.add(o)

    @classmethod
    def bulk_create_or_none(cls, db, iterable, *args, **kwargs):
        try:
            return cls.bulk_create(db, iterable, *args, **kwargs)
        except exc.IntegrityError as e:
            db.rollback()
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


db = SQLAlchemy(model_class=Base)


class Import(db.Model):
    """Imports of basic data done.

    source: '<file FILENAME>', '<uri URI>', 'api'
    """

    __tablename__ = "imports"

    id = Column(Integer, primary_key=True)
    import_start = Column(DateTime, nullable=False)
    import_end = Column(DateTime)
    source = Column(String, nullable=False)
    raw = Column(Text)

    def __repr__(self):
        """Repr."""
        return "<Import {}>".format(self.id)


class Doi(db.Model):
    """Doi model.

    Defines the publication data type with it's methods for useage of the Flask
    ORM.

    date comes as YYYY-MM-DD
    """

    __tablename__ = "dois"

    doi = Column(String(128), primary_key=True, nullable=False, index=True)
    date_published = Column(DateTime())
    import_id = Column(Integer, ForeignKey("imports.id"), nullable=False)
    pmc_id = Column(String(256))
    pm_id = Column(String(256))
    url_doi_new = Column(Boolean, nullable=False)
    url_doi_old = Column(Boolean, nullable=False)
    url_doi_lp = Column(Boolean, nullable=False)
    url_ncbi = Column(Boolean, nullable=False)
    url_pm = Column(Boolean, nullable=False)
    url_pmc = Column(Boolean, nullable=False)
    url_unpaywall = Column(Boolean, nullable=False)
    is_valid = Column(Boolean)

    def __repr__(self):
        """Repr."""
        return "<DOI {}>".format(self.doi)


class Url(db.Model):
    """Url model.

    url_type:   'ojs', 'doi_new', 'doi_old', 'doi_landingpage',
                'unpaywall', 'pm', 'pmc'
    """

    __tablename__ = "urls"

    url = Column(String(512), primary_key=True, index=True)
    doi = Column(String(64), ForeignKey("dois.doi"), nullable=False)
    url_type = Column(String(32))
    date_added = Column(DateTime(), nullable=False)

    def __repr__(self):
        """Repr."""
        return "<URL {}>".format(self.url)


class Request(db.Model):
    """NCBIRequest model."""

    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    doi = Column(String(64), ForeignKey("dois.doi"), nullable=False)
    request_url = Column(String(512))
    request_type = Column(String(32))
    response_content = Column(Text())
    response_status = Column(String)

    def __repr__(self):
        """Repr."""
        return '<API Request "{}">'.format(self.request_type)


class FBRequest(db.Model):
    """FBRequest model."""

    __tablename__ = "fbrequests"

    id = Column(Integer, primary_key=True)
    url_url = Column(String(512), ForeignKey("urls.url"), nullable=False)
    response = Column(Text())
    reactions = Column(Integer)
    shares = Column(Integer)
    comments = Column(Integer)
    plugin_comments = Column(Integer)
    timestamp = Column(DateTime())

    def __repr__(self):
        """Repr."""
        return "<Facebook Request {}>".format(self.request)


class Table2Model:
    IMPORTS = Import()
    DOIS = Doi()
    URLS = Url()
    REQUESTS = Request()
    FBREQUESTS = FBRequest()
