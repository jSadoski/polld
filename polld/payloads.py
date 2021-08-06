import sys
import discord_opcodes as opcode


def gateway_dispatch(data: dict, sequence_number: int, event_name: str):
    return {"op": opcode.DISPATCH, "d": data, "s": sequence_number, "t": event_name}


def heartbeat(last_sequence_number: int = None):
    return {
        "op": opcode.HEARTBEAT,
        "d": last_sequence_number if last_sequence_number else None,
    }


def identify(token: str):
    return {
        "op": opcode.IDENTIFY,
        "d": {
            "token": token,
            "properties": {
                "$os": sys.platform,
                "$browser": "polld",
                "$device": "polld",
            },
            # "compress": True,
            "large_threshold": 250,
            "shard": [0, 1],
            # "presence": {
            #     "activities": [
            #         {
            #             "name": "Cards Against Humanity",
            #             "type": 0,
            #         }
            #     ],
            #     "status": "dnd",
            #     "since": 91879201,
            #     "afk": False,
            # },
            "intents": 21,
        },
    }
