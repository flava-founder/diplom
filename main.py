import sys
import asyncio

import uvicorn

from worker.worker import run
from gpt.server import create_server
from tg_parser.parser import start_parser



if __name__ == '__main__':
    if sys.argv[1] == 'api':
        uvicorn.run(create_server(), host='0.0.0.0')

    if sys.argv[1] == 'tg_parser':
        asyncio.run(start_parser())

    if sys.argv[1] == 'worker':
        asyncio.run(run())

