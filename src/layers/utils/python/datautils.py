import dataclasses
import json


def responseJson(data):
    return json.dumps(dataclasses.asdict(data))


@dataclasses.dataclass
class EntryRegistResponse:
    staus: str = ""
    match_id: str = ""


@dataclasses.dataclass
class MatchingCheckResponse:
    status: str = ""
    is_first: bool = False
    match_id: str = ""


# @dataclasses.dataclass
# class ActionRegistResponse:
#     status: str = ""
#     latest: str = ""
#     history: bool = False


@dataclasses.dataclass
class ActionGetResponse:
    status: str = ""
    latest: str = ""
    history: list = dataclasses.field(default_factory=list)