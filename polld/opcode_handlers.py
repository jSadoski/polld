import logging
import asyncio
from aiohttp import ClientSession, ClientWebSocketResponse
from time import strftime, gmtime
from datetime import datetime
import settings
import discord_opcodes as opcode
import payloads
from models import ConnectionDetails
import pprint

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
        start = datetime.now()
        await asyncio.sleep(heartbeat_interval)
        if condeets.awaiting_heartbeat_ack is True:
            logging.warning(
                f"✘ Heartbeat issued at {start} not Acknowledged, closing connection..."
            )
            await ws.close()


ws_msg_responses = {}


async def opcode_response(
    ws: ClientWebSocketResponse,
    session: ClientSession,
    op: int,
    json_msg: dict,
    condeets: ConnectionDetails = ConnectionDetails(),
):
    if op == opcode.DISPATCH:
        event_type = json_msg["t"]
        data = json_msg["d"]
        if event_type == "READY":
            logger.info("Received Dispatch/Ready State...")
            dispatch = dict(json_msg["d"])
            session_id = str(dispatch["session_id"])
            logger.info(f"Session ID: {session_id}")
            condeets.session_id = session_id
        elif event_type == "INTERACTION_CREATE":
            interaction_id = data["id"]
            interaction_token = data["token"]
            url = (
                f"{settings.DISCORD_API_URL}"
                f"interactions/{interaction_id}/{interaction_token}/callback"
            )

            json = {"type": 4, "data": {"content": "Congrats on sending your command!"}}
            logger.debug(f"Sending response: {pprint.pformat(json)}")
            await session.post(url, json=json)

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
            logging.warning("✘ Session Invalidated, closing connection")
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
