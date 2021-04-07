# !/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
from typing import Type
from typing import Union

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from app.models import Doi
from app.models import FBRequest
from app.models import Import
from app.models import Request
from app.models import Url


DatabaseModels = Type[Union[Import, Doi, Url, Request, FBRequest]]


def get_all(
    db: Session, model: DatabaseModels, skip: int = 0, limit: int = 100,
) -> Query:
    """Get all entries of a model.

    Parameters
    ----------
    db : Session
        SQLAlchemy session.
    model : BaseModel
        model
    skip : int, optional
        Number of entries to be skipped.
    limit : int, optional
        Number of entries to be limited to.

    Returns
    -------
    Query
        Query result.
    """

    return db.session.query(model).offset(skip).limit(limit).all()


def get_first(db: Session, model: DatabaseModels, kwargs: dict) -> Query:
    """Get first entry of a model.

    Parameters
    ----------
    db : Session
        SQLAlchemy session.
    model : BaseModel
        model
    kwargs : dict, optional

    Returns
    -------
    Query
        Query result.
    """
    return db.session.query(model).filter_by(**kwargs).first()


def create_entity(
    db: Session, model: DatabaseModels, kwargs: dict = {}
) -> DatabaseModels:
    """Create one entry of a model.

    Parameters
    ----------
    db : Session
        SQLAlchemy session.
    model : BaseModel
        model
    kwargs : dict, optional

    Returns
    -------
    BaseModel
        model after entry is created.
    """
    db_entity = model(**kwargs)
    db_entity.save(db)
    return db_entity


def create_entities(
    db: Session, model: DatabaseModels, iterable: list, kwargs: dict = {},
) -> DatabaseModels:
    """Create entities of a model.

    Parameters
    ----------
    db : Session
        SQLAlchemy session.
    model : BaseModel
        model
    iterable : list
        Iterable entries.
    kwargs : dict, optional

    Returns
    -------
    BaseModel
        model after entries are created.

    """
    db_entities = model.bulk_create(db, iterable, **kwargs)
    return db_entities
