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


def request_unpaywall_api(url):
    resp = get(url)
    return resp


def get_GraphAPI(api_token, version):
    return GraphAPI(api_token, version=version)


def get_GraphAPI_urls(fb_graph, url_list):
    return fb_graph.get_objects(ids=url_list, fields="engagement,og_object",)


def get_GraphAPI_token(app_id, app_secret):
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
