# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Request functions."""
from facebook import GraphAPI
from requests import get, post
from requests.exceptions import RequestException
from datetime import datetime
from json import loads


def request_doi_landingpage(url):
    # TODO: Fix allow_redirects -> kwargs, params
    return get(url, allow_redirects=True)


def request_ncbi_api(url, ncbi_tool, ncbi_email, doi):
    resp = get(
        url,
        params={
            "tool": ncbi_tool,
            "email": ncbi_email,
            "idtype": "doi",
            "versions": "no",
            "format": "json",
        },
    )
    return resp


def request_unpaywall_api(url):
    resp = get(url)
    return resp


def get_graphapi(api_token):
    return GraphAPI(api_token, version="2.10")


def get_graphapi_urls(fb_graph, url_list):
    return fb_graph.get_objects(ids=url_list, fields="engagement,og_object",)


def get_graphapi_token(app_id, app_secret):
    payload = {
        "grant_type": "client_credentials",
        "client_id": app_id,
        "client_secret": app_secret,
    }
    try:
        response = post(
            "https://graph.facebook.com/oauth/access_token?", params=payload
        )
    except RequestException:
        raise Exception()
        return False
    return loads(response.text)


class Request:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_request(self, url, params=None, auth=False):
        try:
            resp = get(url, params=params)
            return resp
        except:
            print("ERROR: GET - Could not establish connection to api {0}.".format(url))


class HttpRequest(Request):
    def get(url):
        # TODO: Fix allow_redirects -> kwargs, params
        return self.get(url, allow_redirects=True)


class NcbiRequest(Request):
    def get(url, ncbi_tool, ncbi_email, doi):
        resp = self.get(
            url,
            params={
                "tool": ncbi_tool,
                "email": ncbi_email,
                "idtype": "doi",
                "versions": "no",
                "format": "json",
            },
        )
        return resp.json()


class UnpaywallRequest(Request):
    def get(url):
        resp = self.get(url)
        return resp.json()


class FBGraphRequest(Request):
    pass
    # def fb_requests(app_id, app_secret, batch_size):
    #     """Get app access token.
    #
    #     Example Response:
    #     {'id': 'http://dx.doi.org/10.22230/src.2010v1n2a24',
    #     'engagement': { 'share_count': 0, 'comment_plugin_count': 0,
    #                     'reaction_count': 0, 'comment_count': 0}}
    #     """
    #     from app.models import FBRequest
    #     from app.models import Url
    #
    #     payload = {
    #         "grant_type": "client_credentials",
    #         "client_id": app_id,
    #         "client_secret": app_secret,
    #     }
    #     try:
    #         response = requests.post(
    #             "https://graph.facebook.com/oauth/access_token?", params=payload
    #         )
    #     except requests.exceptions.RequestException:
    #         raise Exception()
    #
    #     token = loads(response.text)
    #     fb_graph = GraphAPI(token["access_token"], version="2.10")
    #
    #     fb_request_added = 0
    #     result_url = Url.query.all()
    #
    #     for i in range(0, len(result_url), batch_size):
    #         batch = result_url[i : i + batch_size]
    #         url_list = []
    #         for row in batch:
    #             url_list.append(row.url)
    #         urls_response = fb_graph.get_objects(
    #             ids=url_list, fields="engagement,og_object"
    #         )
    #         for key, value in urls_response.items():
    #             if urls_response:
    #                 db_fb_request = FBRequest(url=key, response=value)
    #                 db.session.add(db_fb_request)
    #                 fb_request_added += 1
    #         db.session.commit()
    #
    #     db.session.close()
    #     print(
    #         "{0} Facebook openGraph request's added to database.".format(fb_request_added)
    #     )
