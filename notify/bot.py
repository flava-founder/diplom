import os
import time
import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from dotenv import load_dotenv
from faststream.redis import RedisBroker

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes


load_dotenv()

logger = logging.getLogger(__name__)

broker = RedisBroker(os.environ.get('REDIS'))
token = os.environ.get('NOTIFY_BOT_TOKEN')
engine = create_async_engine(os.environ.get('DATABASE'))


@broker.subscriber(list='alert')
async def notify(message):
    bot = Bot(token)

    async with engine.begin() as connection:
        extra = (
            await connection.execute(
                text(
                    '''
                    SELECT leak_volume, leak_object, company, details
                    FROM leaks
                    WHERE id = :id
                    '''
                ),
                dict(id=message['id'])
            )
        ).mappings().one_or_none() if message.get('id', None) else None


    to_tg = f'Title: {message["title"]} ({message["source"]})\n\n'
    to_tg += f'Message: \n{message["message"]}\n\n'

    if extra:
        if extra.leak_volume:
            to_tg += f'Volume: <code>{extra.leak_volume}</code>\n'
        if extra.leak_object:
            to_tg += f'Object: <code>{extra.leak_object}</code>\n'
        if extra.company:
            to_tg += f'Company: <code>{extra.company}</code>\n'
        if extra.details:
            to_tg += f'Details: <code>{extra.details}</code>\n'

    await bot.send_message(
        chat_id=-1002362100705,
        text=to_tg,
        parse_mode='HTML',
    )

    logger.info('Sent alert %s', message)

    time.sleep(10)


def start_notify():
    async def post_init(_):
        await broker.start()

    async def post_shutdown(_):
        await broker.close()

    application = ApplicationBuilder().token(
        token
    ).post_init(
        post_init
    ).post_shutdown(
        post_shutdown
    ).build()

    application.run_polling()


if __name__ == '__main__':
    start_notify()
