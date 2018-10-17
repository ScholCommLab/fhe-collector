from app import db
# import datetime


class Publication(db.Model):
    """Publication model.

    Defines the publication data type with it's methods for useage of the Flask ORM.
    """
    doi = db.Column(db.String(64), primary_key=True)
    pub_date = db.Column(db.DateTime())
    origin = db.Column(db.String(256))  # 'import FILENAME' or 'api'
    date_added = db.Column(db.DateTime())

    # def __init__(self, url, doi, date):
    #     self.date = datetime.datetime.strptime(date, '%Y-%m-%d')

    def __repr__(self):
        """Default output method.

        Args:
            None
        """
        return '<Publication {}>'.format(self.doi)


class Url(db.Model):
    url = db.Column(db.String(256), primary_key=True)
    publication_doi = db.Column(db.String(64), db.ForeignKey('publication.doi'), nullable=False)
    url_type = db.Column(db.String(64))  # pubmedcentral, pubmed, doi.org,
    origin = db.Column(db.String(256))  # ncbi, doi.org, 'import FILENAME' or 'api'
    date_added = db.Column(db.DateTime())

    def __repr__(self):
        return '<URL {}>'.format(self.url)


class FBRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_url = db.Column(db.String(256), db.ForeignKey('url.url'), nullable=False)
    request = db.Column(db.Text())
    response = db.Column(db.Text())
    engagement = db.Column(db.Text())
    timestamp = db.Column(db.DateTime())
    error = db.Column(db.Boolean())

    def __repr__(self):
        return '<Facebook Request {}>'.format(self.id)


class NCBIRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_url = db.Column(db.String(256), db.ForeignKey('url.url'), nullable=False)
    request = db.Column(db.Text())
    response = db.Column(db.Text())
    pmcid = db.Column(db.String(64))
    pmid = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime())
    error = db.Column(db.Boolean())

    def __repr__(self):
        return '<NCBI Request {}>'.format(self.id)
