import os
import json
import logging
import requests

from redis.asyncio import from_url
from dotenv import load_dotenv
from telethon.sync import TelegramClient, events, Message


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
redis = from_url(os.environ.get('REDIS'))


async def message(event: Message):
    if event.is_group or event.is_channel:
        await redis.lpush(
            'messages', json.dumps(
                {
                    'message': event.text,
                    'source': event.chat_id,
                    'title': (await event.get_chat()).title,
                }
            )
        )
    else:
        await redis.lpush(
            'messages', json.dumps(
                {
                    'message': event.text,
                    'source': event.chat_id,
                    'title': (await event.get_sender()).username
                }
            )
        )

    logger.info('Push message from %s to queue', event.chat_id)


def start_parser():
    client = TelegramClient('parser_session', api_id, api_hash)
    client.start(phone='79055087953')
    client.on(events.NewMessage())(message)

    client.run_until_disconnected()

