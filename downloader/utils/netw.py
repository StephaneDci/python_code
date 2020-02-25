# -*- coding: utf-8 -*-

import requests
import logging
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-12s %(threadName)s: %(message)s')

def make_get_requests(url: str, verb: str='GET', proxies=None, stream=False, session=None, **kwargs):
    try:

        logging.debug('* Request URL: {}'.format(url))
        logging.debug('* Request method: {}'.format(verb))

        retries = Retry(total=6, backoff_factor=1, connect=5,
                        status=3, status_forcelist=[400, 401, 404, 500, 501, 502])

        # Prepare the request with Retry
        if session is None:
            session = requests.Session()

        session.mount("http://", HTTPAdapter(max_retries=retries, pool_maxsize=20))
        session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=20))

        res = None
        if verb.upper() == 'GET':
            res = session.get(url, stream=stream, proxies=proxies)
        elif verb.upper() == 'HEAD':
            res = session.head(url, stream=stream, proxies=proxies)
        else:
            raise Exception("Method NOT ALLOWED")

        if isinstance(res, Response):
            res.raise_for_status()
        # N'atteindra par ce code Si statut HTTP dans status_forcelist
        #session.close()
        return res

    # Request Exception Handling
    except MaxRetryError as maxer:
        logging.error(f"FATAL : Max Retries Error: {maxer} on {url}")
    except (HTTPError, ConnectionError, Timeout, RequestException) as err:
        logging.error(f"FATAL : Connection Error: {err} on {url}")
