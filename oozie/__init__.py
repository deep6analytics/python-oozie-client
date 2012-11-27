#!/usr/bin/env python

import logging
import os
import requests

from . import workflow

class ClientError(Exception):
    pass

class ServerError(Exception):
    pass

class client(object):
    def __init__(self, url=None):
        if url is None:
            url = os.environ.get('OOZIE_URL')
        if url is None:
            raise ClientError('No Oozie URL provided and none set in environment OOZIE_URL')
        self._url = url
    def healthcheck(self):
        try:
            systemMode = requests.get(self._url + 'v1/admin/status').json['systemMode']
            assert(systemMode == 'NORMAL')
            logging.info('Oozie installation at ' + self._url + ' appears operational')
            return True
        except AssertionError:
            raise ServerError(systemMode)
        except ValueError as e:
            raise ClientError(e.message)
        except urllib2.HTTPError as e:
            raise ClientError('HTTP Error ' + str(e.getcode()) + ': ' + e.msg + ' ' + e.geturl())
    def run(self, workflow):
        # Validate workflow
        
        # Submit job
        pass