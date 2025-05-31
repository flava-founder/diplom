import asyncio
import os
import time

from dotenv import load_dotenv
from faststream.redis import RedisBroker

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes


load_dotenv()


broker = RedisBroker(os.environ.get('REDIS'))
token = os.environ.get('NOTIFY_BOT_TOKEN')


@broker.subscriber(list='alert')
async def notify(message):
    bot = Bot(token)

    await bot.se


def main():
    async def post_init(_):
        await broker.start()

    async def post_shutdown(_):
        await broker.close()

    application = ApplicationBuilder().token(
        os.environ.get()
    ).post_init(
        post_init
    ).post_shutdown(
        post_shutdown
    ).build()

    application.run_polling()


if __name__ == '__main__':
    main()
