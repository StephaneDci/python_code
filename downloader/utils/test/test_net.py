# -*- coding: utf-8 -*-

import unittest
from requests import Session
from unittest.mock import patch
from downloader.utils.netw import make_get_requests

# https://medium.com/@sarit.r/mock-requests-session-fe14d9cd2b6a


class TestUtilsNetworking(unittest.TestCase):

    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code
            self.content = "Mock content"

    @patch.object(Session, 'get', return_value=MockResponse(200))
    def test_request_url_1(self, mock_session):
        r = make_get_requests('http://www.fakeurl', 'GET')
        self.assertEqual(200, r.status_code)
        self.assertEqual("Mock content", r.content)

    @patch.object(Session, 'get', return_value=MockResponse(500))
    def test_request_url_2(self, mock_session):
        r = make_get_requests('http://www.fakeurl', 'GET')
        self.assertEqual(500, r.status_code)
        self.assertEqual("Mock content", r.content)

    @patch.object(Session, 'get', return_value=MockResponse(200))
    def test_request_url_errors(self, mock_session):
        with self.assertRaises(Exception):
            make_get_requests('http://www.fakeurl', 'WRONG')



