import datetime
import importlib
import os
from zoneinfo import ZoneInfo

import boto3

import logger
from aws.gatherings import Gatherings
from aws.settings import Settings
from service.team_gather_service import TeamGatherService
from service.time_parser import TimeParser
from telegram.api.telegram_api import Telegram


def handler(event, context):
    logger.set_logging_level(os.environ.get('LOGGING_LEVEL', 'INFO'))

    dynamodb_client = boto3.client('dynamodb')
    settings = Settings(dynamodb_client)
    gatherings = Gatherings(dynamodb_client)

    try:
        i18n = importlib.import_module(f'i18n.{settings.locale}')
    except ModuleNotFoundError:
        i18n = importlib.import_module('i18n.en')

    timezone = ZoneInfo(settings.timezone)
    current_time = int(datetime.datetime.now().timestamp())
    time_parser = TimeParser(current_time, timezone)

    if settings.last_update_time + 6 * 24 * 60 * 60 < current_time:
        settings.last_update_id = -1
    settings.last_update_time = current_time

    telegram = Telegram(os.environ['TELEGRAM_TOKEN'])

    team_gather_service = TeamGatherService(telegram, settings, gatherings, i18n, time_parser)
    team_gather_service.handle_events()

    settings.save()
