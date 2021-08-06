import logging
from typing import Any, List, Union
import aiohttp
import asyncio
from aiohttp.client import ClientSession
from time import strftime, gmtime
from aiohttp.client_ws import ClientWebSocketResponse
from yarl import URL
import settings
import discord_opcodes as opcode
import payloads
import codecs
from datetime import datetime


class Application:
    id_: int
    flags: int


class User:
    verified: bool
    username: str
    mfa_enabled: bool
    id_: int
    flags: int
    email: str
    discriminator: int
    bot: bool
    avatar: str


class Dispatch:
    user: User
    user_settings: dict
    shard: List[int]
    session_id: str
    relationships: List[Any]
    private_channels: List[int]
    presences: List[Any]
    guilds: List[int]
    guild_join_requests: List[Any]
    geo_ordered_rtc_regions: List[str]


class ConnectionDetails:
    dispatch: dict
    hearbeat_interval: int
    last_sequence_number: Union[int, None] = None
    awaiting_heartbeat_ack: bool = False


logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def heartbeat_loop(
    ws: ClientWebSocketResponse,
    heartbeat_interval: int,
    last_sequence_number: int = None,
    condeets: ConnectionDetails = ConnectionDetails(),
):
    logger.info(
        f"❤️ Heartbeat started: {heartbeat_interval}ms"
        f" ({strftime('%H:%M:%S', gmtime(125))})"
    )
    while True:
        logger.info("❤️ Heartbeat!")
        await ws.send_json(payloads.heartbeat(last_sequence_number))
        now = datetime.now()
        await asyncio.sleep(heartbeat_interval)
        if condeets.awaiting_heartbeat_ack is True:
            logging.info(
                f"✘ Heartbeat issued at {now} not Acknowledged, closing connection..."
            )
            await ws.close()


async def opcode_response(
    ws: ClientWebSocketResponse,
    op: int,
    json_msg: dict,
    condeets: ConnectionDetails = ConnectionDetails(),
):
    if op == opcode.DISPATCH:
        logger.info("Received Dispatch...")
        condeets.dispatch = json_msg["d"]

    elif op == opcode.HEARTBEAT:
        logger.debug("❤️ Received Heartbeat...")

    elif op == opcode.PRESENCE:
        # TODO
        logger.debug(json_msg)

    elif op == opcode.RESUME:
        # TODO
        logger.debug(json_msg)

    elif op == opcode.RECONNECT:
        # TODO
        logger.debug(json_msg)

    elif op == opcode.INVALIDATE_SESSION:
        d: bool = json_msg["d"]
        # TODO Reconnect session if d == True
        if d is False:
            logging.info("✘ Session Invalidated, closing connection")
            await ws.close()

    elif op == opcode.HELLO:
        logger.info("Got Hello...")
        condeets.hearbeat_interval = int(json_msg["d"]["heartbeat_interval"])
        logger.info(
            f"Heartbeat inerval: {condeets.hearbeat_interval}ms"
            f" ({strftime('%H:%M:%S', gmtime(125))})"
        )
        asyncio.create_task(
            heartbeat_loop(ws, condeets.hearbeat_interval), name="heartbeat_loop"
        )
        logger.info("Identifying...")
        await ws.send_json(payloads.identify(settings.BOT_TOKEN))

    elif op == opcode.HEARTBEAT_ACK:
        logger.info("❤️ Received Heartbeat Acknowledgement...")
        condeets.awaiting_heartbeat_ack = False

    elif op == opcode.GUILD_SYNC:
        # TODO
        logger.debug(json_msg)

    else:
        logger.warning(f"Got something funny: {json_msg}")


async def discord_socket(session: ClientSession, gateway: str):

    gateway_with_query = URL(gateway).with_query(
        {"v": settings.DISCORD_GATEWAY_VERSION, "encoding": "json"}
    )
    logger.info(f"Websocket connecting to: {gateway_with_query}")

    async with session.ws_connect(gateway_with_query) as ws:
        condeets = ConnectionDetails()
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                json_msg = msg.json()
                logger.debug(f"JSON Message Recieved: {json_msg}")
                op = json_msg["op"]
                await opcode_response(ws, op, json_msg, condeets)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                logger.warning(codecs.decode(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.error(msg.data)
                break
            else:
                logging.warn(f"Got something weird: {msg.type} - {msg.data}")


async def main():
    async with aiohttp.ClientSession(auto_decompress=True) as session:
        async with session.get(f"{settings.DISCORD_API_URL}gateway") as response:
            assert response.status == 200
            response_body = await response.json()
            assert "url" in response_body
            gateway = response_body["url"]
            logger.info(f"Got gateway: {gateway}")

            await discord_socket(session, gateway)


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
