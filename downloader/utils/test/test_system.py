# -*- coding: utf-8 -*-

import unittest
from requests import Session
from unittest.mock import patch
from downloader.utils.system import verify_if_file_exists

# https://medium.com/@sarit.r/mock-requests-session-fe14d9cd2b6a


class TestUtilsSystem(unittest.TestCase):


    @patch('utils.system.os.path.isfile')
    def test_request_url_1(self, mock_file):
        mock_file.return_value = True
        status, msg = verify_if_file_exists('file1')
        self.assertEqual(True, status)




