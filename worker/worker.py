import asyncio
import os
import json
import logging

from redis.asyncio import from_url
from dotenv import load_dotenv
from aiohttp import ClientSession

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)

redis = from_url(os.environ.get('REDIS'))
api_url = os.environ.get('API_URL').strip('/')
engine = create_async_engine(os.environ.get('DATABASE'))


async def run():
    while message := await redis.brpop(['messages']):
        _, data = message
        data = json.loads(data)
        logger.info('Got %s', data)

        async with ClientSession(base_url=api_url) as session:
            async with session.post('/detect', json={'text': data['message']}) as response:
                if response.status != 200:
                    await redis.lpush('messages', json.dumps(data, ensure_ascii=False))
                    logger.info('API returned %s. Return message to queue', response.status_code)
                    await asyncio.sleep(60)
                else:
                    answer = await response.json()

                    logger.info(
                        'Leak: %s, message: %s', data, answer['leak_detected']
                    )

                    async with engine.begin() as connection:
                        query = await connection.execute(
                            text(
                                '''
                                INSERT INTO leaks (
                                    leak_detected, leak_volume, leak_object, company, details,
                                    source, title, "content"
                                ) VALUES (
                                    :leak_detected, :leak_volume, :leak_object, :company, :details,
                                    :source, :title, :content
                                )
                                RETURNING id
                                '''
                            ), dict(
                                leak_detected=answer['leak_detected'],
                                leak_volume=answer.get('leak_volume', None) or None,
                                leak_object=answer.get('leak_object', None) or None,
                                company=answer.get('company', None) or None,
                                details=answer.get('details', None) or None,
                                source=data['source'],
                                title=data['title'],
                                content=data['message']
                            )
                        )
                        msg_id = query.scalar()

                    logger.info('Saved %s', data)

                    if answer['leak_detected']:
                        data['id'] = msg_id
                        await redis.lpush(
                            'alert', json.dumps(data, ensure_ascii=False)
                        )
                        logger.info('Sent to alert bot %s', data)
