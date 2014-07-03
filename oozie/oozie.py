import logging
import os
import os.path
import urllib2

import requests
from . import errors


# Attempt to coerce a given input to an XML buffer
def xmlFromInput(inputData):
    if os.path.exists(inputData):
        with open(inputData, 'r') as f:
            return f.read()
    else:
        return inputData


def expectCode(response, expectedCode, action):
    try:
        assert response.status_code == expectedCode
    except AssertionError:
        if response.status_code == 401:
            raise errors.ClientError(
                'Permission denied when ' + action + ' at ' + response.url + '\nMessage was ' + str(
                    response.status_code) + ':\n' + response.text)
        elif response.status_code >= 400 and response.status_code < 500:
            raise errors.ClientError('Malformed input when ' + action + ' at ' + response.url + '\nMessage was ' + str(
                response.status_code) + ':\n' + response.text)
        else:
            raise errors.ServerError(
                'Unexpected status code when ' + action + ' at ' + response.url + '\nMessage was ' + str(
                    response.status_code) + ':\n' + response.text)


def expectJsonFields(response, expectedFields, action):
    try:
        assert response.json() is not None
        for field in expectedFields:
            assert field in response.json()
    except AssertionError:
        raise errors.ServerError('Malformed response when ' + action + ' at ' + response.url + '\nMessage was ' + str(
            response.status_code) + ':\n' + response.text)


class client(object):
    def __init__(self, url=None):
        if url is None:
            url = os.environ.get('OOZIE_URL')
        if url is None:
            raise errors.ClientError('No Oozie URL provided and none set in environment OOZIE_URL')
        self._url = url.rstrip('/')
        self._version = 'v1'

    def healthcheck(self):
        response = requests.get(
            url='/'.join([self._url, self._version, 'admin/status'])
        )
        try:
            expectCode(response, 200, 'performing healthcheck')
            expectJsonFields(response, ['systemMode'], 'performing healthcheck')
            assert response.json()['systemMode'] == 'NORMAL'
            logging.info('Oozie installation at ' + self._url + ' appears operational')
            return True
        except AssertionError:
            raise errors.ServerError('Oozie server reports ' + response.json()['systemMode'])
        except ValueError as e:
            raise errors.ClientError(e.message)
        except urllib2.HTTPError as e:
            raise errors.ClientError('HTTP Error ' + str(e.getcode()) + ': ' + e.msg + ' ' + e.geturl())

    def config(self):
        response = requests.get(
            url='/'.join([self._url, self._version, 'admin/configuration']),
        )
        expectCode(response, 200, 'retrieving Oozie configuration')
        expectJsonFields(response, [], 'retrieving Oozie configuration')
        return response.json()

    def list(self):
        response = requests.get(
            url='/'.join([self._url, self._version, 'jobs']),
        )
        expectCode(response, 200, 'listing jobs')
        expectJsonFields(response, ['workflows'], 'listing jobs')
        return [wf['id'] for wf in response.json()['workflows']]

    # 
    def submit(self, configuration):
        response = requests.post(
            url='/'.join([self._url, self._version, 'jobs']),
            data=xmlFromInput(configuration),
            headers={'content-type': 'application/xml'},
        )
        expectCode(response, 201, 'submitting job')
        expectJsonFields(response, ['id'], 'submitting job')
        return response.json()['id']

    def run(self, jobId):
        response = requests.put(
            url='/'.join([self._url, self._version, 'job', jobId]),
            params={'action': 'start'},
        )
        expectCode(response, 200, 'running job')
        return True

    def suspend(self, jobId):
        response = requests.put(
            url='/'.join([self._url, self._version, 'job', jobId]),
            params={'action': 'suspend'},
        )
        expectCode(response, 200, 'suspending job')
        return True

    def resume(self, jobId):
        response = requests.put(
            url='/'.join([self._url, self._version, 'job', jobId]),
            params={'action': 'resume'},
        )
        expectCode(response, 200, 'resuming job')
        return True

    def status(self, jobId):
        response = requests.get(
            url='/'.join([self._url, self._version, 'job', jobId]),
        )
        expectCode(response, 200, 'querying job status')
        expectJsonFields(response, ['status'], 'querying job status')
        return response.json()['status']

    def error(self, jobId):
        response = requests.get(
            url='/'.join([self._url, self._version, 'job', jobId]),
        )
        expectCode(response, 200, 'listing job errors')
        expectJsonFields(response, ['actions'], 'listing job errors')
        for action in response.json()['actions']:
            if action['errorMessage'] is not None:
                return action['errorMessage']
        return None
