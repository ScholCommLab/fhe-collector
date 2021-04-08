# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Request functions."""
from json import loads

from facebook import GraphAPI
from requests import get
from requests import post
from requests import Response
from requests.exceptions import RequestException
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning


disable_warnings(InsecureRequestWarning)


def request_doi_landingpage(url: str) -> Response:
    # TODO: Fix allow_redirects -> kwargs, params
    return get(url, allow_redirects=True, verify=False)


def request_ncbi_api(url: str, ncbi_tool: str, ncbi_email: str) -> Response:
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


def request_unpaywall_api(url: str) -> Response:
    resp = get(url)
    return resp


def get_graph_api(fb_api_token: str, version: str) -> GraphAPI:
    return GraphAPI(fb_api_token, version=version)


def get_graph_api_urls(fb_graph: GraphAPI, url_list: list) -> dict:
    return fb_graph.get_objects(ids=url_list, fields="engagement,og_object",)


def get_graph_api_token(app_id: str, app_secret: str) -> dict:
    payload = {
        "grant_type": "client_credentials",
        "client_id": app_id,
        "client_secret": app_secret,
    }
    try:
        response = post(
            "https://graph.facebook.com/oauth/access_token?", params=payload
        )
        return loads(response.text)
    except RequestException:
        raise Exception()
