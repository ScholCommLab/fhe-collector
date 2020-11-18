# !/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from app.models import BaseModel


def get_all(db: Session, model: BaseModel, skip: int = 0, limit: int = 100,) -> Query:
    return db.session.query(model).offset(skip).limit(limit).all()


def get_first(db: Session, model: BaseModel, kwargs: dict) -> Query:
    return db.session.query(model).filter_by(**kwargs).first()


def create_entity(db: Session, model: BaseModel, kwargs: dict) -> BaseModel:
    db_entity = model(**kwargs)
    db_entity.save(db)
    return db_entity


def create_entities(
    db: Session, model: BaseModel, iterable: list, kwargs: dict = {},
) -> BaseModel:
    db_entities = model.bulk_create(db, iterable, **kwargs)
    return db_entities
