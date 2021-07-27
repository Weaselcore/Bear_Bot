from dataclasses import dataclass


# This creates an immutable dataclass. You can get the values through dot notation but cannot change values.
import DateTime


@dataclass(frozen=True)
class PlayerDatabaseInfo:

    id: int
    nickname: str = None
    money_amount: int = 0
    bank_amount: int = 0
    last_stolen_id: int = None
    last_redeemed: DateTime.DateTime = None
    last_bank_time: DateTime.DateTime = None
    last_stolen_time: DateTime.DateTime = None
    total_gained: int = 0
    total_lost: int = 0
