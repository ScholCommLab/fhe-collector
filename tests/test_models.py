# import pytest
# from app.models import db, Publication
#
# create_user = False
#
#
# @pytest.mark.usefixtures("testapp")
# class TestModels:
#     def test_pub_save(self, testapp):
#         """ Test Saving the publication model to the database """
#
#         pub = Publication('http://src-online.ca/index.php/src/article/view/3', '10.22230/src.2010v1n1a3')
#         db.session.add(pub)
#         db.session.commit()
#
#         pub = Publication.query.filter_by(doi='10.22230/src.2010v1n1a3').first()
#         assert pub is not None
