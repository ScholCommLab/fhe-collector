from app import db
import datetime


class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128))
    doi = db.Column(db.String(64), index=True)
    date = db.Column(db.Date())
    doi_url = db.Column(db.String(128))
    doi_resolve_ts = db.Column(db.Date())
    doi_resolve_status = db.Column(db.String(128))
    doi_resolve_error = db.Column(db.String(128))
    pmid = db.Column(db.String(128))
    pmc = db.Column(db.String(128))
    ncbi_ts = db.Column(db.Date())
    ncbi_errmsg = db.Column(db.String(128))

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
