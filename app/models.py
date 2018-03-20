from app import db
import datetime


class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128))
    doi = db.Column(db.String(64), index=True)
    date = db.Column(db.Date())

    def __init__(self, url, doi, date):
        self.url = url
        self.doi = doi
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d')

    def __repr__(self):
        return '<Publication {}>'.format(self.doi)


class FacebookResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Facebook Response {}>'.format(self.id)


class AltmetricsResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Altmetrics Response {}>'.format(self.id)


class CrossRefResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<CrossRef Response {}>'.format(self.id)
