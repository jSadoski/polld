from typing import Any, List, Tuple, Union

from attr import dataclass


""" Discord Models """


class Application:
    def init(self, id: int, flags: int, **kwargs):
        self.id = id
        self.flags = flags
        for key, value in kwargs:
            setattr(self, key, value)


@dataclass
class ApplicationCommandOptionChoices:
    name: str
    value: Union[str, int, float]


@dataclass
class ApplicationCommandOption:
    type: int  # value of application command option type
    name: str  # 1-32 lowercase character name matching ^[\w-]{1,32}$
    description: str  # 1-100 character description
    required: bool = False  # if the parameter is required or optional--default false
    # Array of application command option choice choices for STRING, INTEGER, and
    # NUMBER types for the user to pick from
    choices: List[ApplicationCommandOptionChoices] = []
    # Array of application command option if the option is a subcommand or subcommand
    # group type, this nested options will be the parameters
    options: List = []


@dataclass
class ApplicationCommand:
    name: str
    description: str
    options: List[ApplicationCommandOption] = []
    default_permissions: bool = True


class User:
    def __init__(
        self,
        id_: int,
        username: str,
        avatar: str = None,
        discriminator: str = None,
        **kwargs,
    ):
        self.id_ = id_
        self.username = username
        self.avatar = avatar
        self.discriminator = discriminator
        for key, value in kwargs:
            setattr(self, key, value)


class UnavailableGuild:
    id_: int
    unavailable: bool


""" App Models """


class ConnectionDetails:
    hearbeat_interval: int
    awaiting_heartbeat_ack: bool = False
    last_sequence_number: Union[int, None]
    user: User
    user_settings: dict
    guilds: List[UnavailableGuild]
    session_id: str
    shard: Tuple[int, int]
    application: Application
    relationships: List[Any]
    private_channels: List[int]
    presences: List[Any]
    guild_join_requests: List[Any]
    geo_ordered_rtc_regions: List[str]
