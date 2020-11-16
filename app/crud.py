# !/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
from typing import Union
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from app.models import Import, Doi, Url, Request, FBRequest
from app.models import Base


def get_all(
    db: Session,
    model: Union[Import, Doi, Url, Request, FBRequest],
    skip: int = 0,
    limit: int = 100,
) -> Query:
    return db.query(model).offset(skip).limit(limit).all()


def get_first(
    db: Session, model: Union[Import, Doi, Url, Request, FBRequest], kwargs: dict
) -> Query:
    return db.query(model).filter_by(**kwargs).first()


def create_entity(
    db: Session, model: Union[Import, Doi, Url, Request, FBRequest], kwargs: dict
) -> Base:
    db_entity = model(**kwargs)
    db_entity.save(db)
    return db_entity


def create_entities(
    db: Session,
    model: Union[Import, Doi, Url, Request, FBRequest],
    iterable: list,
    kwargs: dict,
) -> Query:
    db_entities = model.bulk_create(db, iterable, **kwargs)
    return db_entities
