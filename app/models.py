from app import db
from datetime import datetime


class Doi(db.Model):
    """Publication model.

    Defines the publication data type with it's methods for useage of the Flask ORM.
    """
    doi = db.Column(db.String(64), primary_key=True)
    imported_at = db.Column(db.DateTime())
    source_type = db.Column(db.String(256))  # file or api
    source_json = db.Column(db.Text())  # raw json from api endpoint
    source_file = db.Column(db.String(256))  # filename

    def __init__(self, doi, source_type, source_file, source_json):
        self.doi = doi
        self.source_type = source_type
        self.source_json = source_json
        self.source_file = source_file
        self.imported_at = datetime.now()

    def __repr__(self):
        """Default output method.

        """
        return '<DOI {}>'.format(self.doi)


# class Url(db.Model):
#     url = db.Column(db.String(256), primary_key=True)
#     publication_doi = db.Column(db.String(64), db.ForeignKey('publication.doi'), nullable=False)
#     url_type = db.Column(db.String(64))  # pubmedcentral, pubmed, doi.org,
#     origin = db.Column(db.String(256))  # ncbi, doi.org, 'import FILENAME' or 'api'
#     date_added = db.Column(db.DateTime())
#
#     def __repr__(self):
#         return '<URL {}>'.format(self.url)


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
