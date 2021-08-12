import logging
import aiohttp
import asyncio
from aiohttp import ClientSession
from yarl import URL
import codecs
import pprint
import settings
from models import ConnectionDetails
from opcode_handlers import opcode_response


logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def discord_socket(session: ClientSession, gateway_uri: str):
    gateway_with_query = URL(gateway_uri).with_query(
        {"v": settings.DISCORD_GATEWAY_VERSION, "encoding": "json"}
    )
    logger.info(f"Websocket connecting to: {gateway_with_query}")

    async with session.ws_connect(gateway_with_query) as ws:
        condeets = ConnectionDetails()
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                json_msg: dict = msg.json()
                logger.debug(f"JSON Message Recieved:\n{pprint.pformat(json_msg)}")
                op = int(json_msg["op"])
                await opcode_response(ws, session, op, json_msg, condeets)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                logger.warning(codecs.decode(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.error(msg.data)
                break
            else:
                logging.warn(f"Got something weird: {msg.type} - {msg.data}")


async def main():
    async with ClientSession(auto_decompress=True) as session:
        async with session.get(f"{settings.DISCORD_API_URL}gateway") as response:
            assert response.status == 200
            response_body = await response.json()
            assert "url" in response_body
            gateway_uri = response_body["url"]
            logger.info(f"Got gateway: {gateway_uri}")

            await discord_socket(session, gateway_uri)


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
