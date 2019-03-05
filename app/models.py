from app import db
from datetime import datetime


class Import(db.Model):
    """Imports of basic data done."""
    id = db.Column(db.Integer, primary_key=True)
    imported_at = db.Column(db.DateTime(), nullable=False)
    source = db.Column(db.String(512), nullable=False)  # '<file FILENAME>', '<uri URI>', 'api'
    raw = db.Column(db.Text())

    def __init__(self, source, raw):
        self.source = source
        self.raw = raw
        self.imported_at = datetime.now()

    def __repr__(self):
        """Default output method."""
        return '<Import {}>'.format(self.id)


class Doi(db.Model):
    """Doi model.

    Defines the publication data type with it's methods for useage of the Flask
    ORM.
    """
    doi = db.Column(db.String(64), primary_key=True, nullable=False)
    pmc_id = db.Column(db.String(256), unique=True)
    pm_id = db.Column(db.String(256), unique=True)
    import_id = db.Column(db.Integer, db.ForeignKey('import.id'), nullable=False)

    def __init__(self, doi, import_id):
        self.doi = doi
        self.import_id = import_id

    def __repr__(self):
        """Default output method.

        """
        return '<DOI {}>'.format(self.doi)


class Url(db.Model):
    """Url model."""
    url = db.Column(db.String(512), primary_key=True)
    doi = db.Column(db.String(64), db.ForeignKey('doi.doi'), nullable=False)
    url_type = db.Column(db.String(32), nullable=False)  # 'ojs', 'doi_new', 'doi_old', 'crossref', 'unpaywall', 'pubmed', 'pubmedcentral'
    date_added = db.Column(db.DateTime(), nullable=False)

    def __init__(self, url, doi, url_type):
        self.url = url
        self.doi = doi
        self.url_type = url_type
        self.date_added = datetime.now()

    def __repr__(self):
        return '<URL {}>'.format(self.url)


# class FBRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     url_url = db.Column(db.String(256), db.ForeignKey('url.url'), nullable=False)
#     request = db.Column(db.Text())
#     response = db.Column(db.Text())
#     engagement = db.Column(db.Text())
#     timestamp = db.Column(db.DateTime())
#     error = db.Column(db.Boolean())
#
#     def __repr__(self):
#         return '<Facebook Request {}>'.format(self.id)
