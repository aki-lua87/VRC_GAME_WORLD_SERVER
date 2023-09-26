import dataclasses
import json


def responseJson(data):
    return json.dumps(dataclasses.asdict(data))


@dataclasses.dataclass
class EntryRegistResponse:
    status: str = ""
    match_id: str = ""


@dataclasses.dataclass
class MatchingCheckResponse:
    status: str = ""
    is_first: bool = False
    match_id: str = ""
    opponent_user_id: str = ""


@dataclasses.dataclass
class ActionRegistResponse:
    status: str = ""
    latest: str = ""
    history: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ActionGetResponse:
    status: str = ""
    latest: str = ""
    history: list = dataclasses.field(default_factory=list)


# 状態
STATUS_ENTRYED = 'ENTRYED'  # エントリー済み、かつマッチング前
STATUS_MATCHED = 'MATCHED'  # 対戦中
STATUS_CANCELED = 'CANCELED'  # リセット押下、または不明なエラー
STATUS_FINISHED = 'FINISHED'  # 現状これに遷移できない
