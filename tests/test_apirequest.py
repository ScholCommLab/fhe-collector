import os
from app import create_app


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class TestAPIRequests:
    def test_nbci_request(self, import_ncbi):
        """
        Tests if the app starts correctly.
        """
        from app import request_ncbi_api
        import urllib.parse

        data = import_ncbi
        app = create_app()

        for entry in data:
            doi_url_encoded = urllib.parse.quote(entry[0])
            url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={0}".format(
                doi_url_encoded
            )
            print(app.config["NCBI_TOOL"])
            resp_data = request_ncbi_api(
                url, app.config["NCBI_TOOL"], app.config["APP_EMAIL"], entry[0]
            )
            if entry[3] == "ok":
                print(resp_data)
                assert resp_data["status"] == "ok"
                assert resp_data["records"][0]["doi"] == entry[0]
                assert resp_data["records"][0]["pmid"] == entry[1]
                assert resp_data["records"][0]["pmcid"] == entry[2]
            else:
                assert resp_data["status"] == "ok"
                assert resp_data["records"][0]["doi"] == entry[0]
                assert resp_data["records"][0]["status"] == entry[3]

    def test_doi_lp_request(self, import_doi_landingpage):
        """
        Tests if doi landingpage request works.
        """
        from app import request_doi_landingpage_api
        import urllib.parse

        data = import_doi_landingpage

        for entry in data:
            doi_url_encoded = urllib.parse.quote(entry[0])
            url = "https://doi.org/{0}".format(doi_url_encoded)
            resp = request_doi_landingpage_api(url)
            resp_url = resp.url
            if resp.url:
                assert entry[1] == resp_url
