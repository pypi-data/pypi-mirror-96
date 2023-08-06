import datetime
import json
import logging
import os
import pathlib
import tempfile

import google.cloud.logging
import requests

import dcyd.utils.utils as utils
import dcyd.gcl_patch as gcl_patch


class ExtractMsgFormatter(logging.Formatter):
    def format(self, record):
        return record.msg


def request_service_account_key():
    '''
    Request the latest GCP service account key and write it to a temp file.
    '''
    project_credentials = utils.get_project_credentials()

    if not project_credentials['project_id']:
        raise RuntimeError('project id is missing')

    if not project_credentials['project_access_token']:
        raise RuntimeError('project access token is missing')

    response = requests.post(
        utils.api_url('/service_account_key'),
        json=project_credentials,
    )

    if not response.ok:
        logging.error(response.text)
        raise Exception("Failed to request service account key")

    response_json = response.json()
    key_file_path = os.path.join(tempfile.gettempdir(), 'dcyd_gcsak.json')
    pathlib.Path(key_file_path).write_text(response.text)
    return key_file_path


def get_gcp_logger():
    '''
    Initialize a GCP logger.

    TODO: add error handling
    TODO: extra the client initialization logic
    '''
    key_file_path = request_service_account_key()
    client = google.cloud.logging.Client.from_service_account_json(key_file_path)

    handler = google.cloud.logging.handlers.handlers.CloudLoggingHandler(
        client=client,
        name='mpm-client-log', #NOTE: This logger name is critical for downstream data processing. Do not change
        transport=gcl_patch.BackgroundThreadTransport,
    )
    handler.setFormatter(ExtractMsgFormatter())

    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    logger.addHandler(handler)
    return logger

GCP_LOGGER = get_gcp_logger()

FILE_LOGGER_ENABLED = os.getenv('MPM_FILE_LOGGER', '') == 'true'

def get_file_logger():
    '''
    Initialize a file logger
    '''
    logger = logging.getLogger('mpm-client-log')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('mpm-client-log.log') if FILE_LOGGER_ENABLED else logging.NullHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

FILE_LOGGER = get_file_logger()

def log_struct(record: dict):
    '''
    Write a dictionary to GCP Logging
    '''
    if FILE_LOGGER_ENABLED:
        FILE_LOGGER.info(json.dumps({
            'jsonPayload': {**record},
        }))
    return GCP_LOGGER.log(level=logging.INFO, msg=record)

