import os
import pytest

from app import create_app


@pytest.fixture()
def testapp():
    os.environ['YOURAPPLICATION_MODE'] = 'testing'
    app = create_app()
    client = app.test_client()

    return client
