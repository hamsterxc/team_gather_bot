import datetime
import importlib
import os
import time
from zoneinfo import ZoneInfo

import boto3

import logger
from aws.gatherings import Gatherings
from aws.settings import Settings
from service.team_gather_service import TeamGatherService
from service.time_parser import TimeParser
from telegram.api.telegram_api import Telegram
from telegram.api.telegram_exception import TelegramException


class Handler:
    def __init__(self, dynamodb_client, telegram):
        self.dynamodb_client = dynamodb_client
        self.telegram = telegram

    def handle(self):
        logger.debug("Start")

        settings = Settings(self.dynamodb_client)
        gatherings = Gatherings(self.dynamodb_client)

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

        team_gather_service = TeamGatherService(self.telegram, settings, gatherings, i18n, time_parser)
        team_gather_service.handle_events()

        settings.save()

        logger.debug("End")


def handler(event, context):
    logger.set_logging_level(os.environ.get('LOGGING_LEVEL', 'INFO'))

    dynamodb_client = boto3.client('dynamodb')
    telegram = Telegram(os.environ['TELEGRAM_TOKEN'])
    handler = Handler(dynamodb_client, telegram)

    execution_timeout = int(os.environ.get('EXECUTION_TIMEOUT', '1'))
    time_between_invocations = int(os.environ.get('TIME_BETWEEN_INVOCATIONS', '2'))
    time_start = time.time()
    while time.time() - time_start < execution_timeout:
        try:
            handler.handle()
        except TelegramException as e:
            logger.error(str(e))

        if time.time() - time_start < execution_timeout - time_between_invocations:
            time.sleep(time_between_invocations)
        else:
            break
