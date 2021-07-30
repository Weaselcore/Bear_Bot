from typing import Union
from collections import namedtuple

from bblib.Util import get_row
from bblib.core.player_database_info import PlayerDatabaseInfo


class PlayerInfoFactory:

    @staticmethod
    def generate(member_id: int) -> Union[None, PlayerDatabaseInfo]:

        # Converting tuple into namedtuple makes making the PlayerDatabaseInfo more readable.
        PlayerData = namedtuple("PlayerData",
                                ["id",
                                 "nickname",
                                 "money_amount",
                                 "bank_amount",
                                 "last_stolen_id",
                                 "last_redeemed",
                                 "last_bank_time",
                                 "last_stolen_time",
                                 "total_gained",
                                 "total_lost"])

        # Grabs result tuple from a row in the Sqlite3 database using member_id.
        result = get_row(member_id)
        if result is not None:
            player_named_tuple = PlayerData._make(result)
            player_info = PlayerDatabaseInfo(id=player_named_tuple.id,
                                             nickname=player_named_tuple.nickname,
                                             money_amount=player_named_tuple.money_amount,
                                             bank_amount=player_named_tuple.bank_amount,
                                             last_stolen_id=player_named_tuple.last_stolen_id,
                                             last_redeemed=player_named_tuple.last_redeemed,
                                             last_bank_time=player_named_tuple.last_bank_time,
                                             last_stolen_time=player_named_tuple.last_stolen_time,
                                             total_gained=player_named_tuple.total_gained,
                                             total_lost=player_named_tuple.total_lost)
            return player_info
        else:
            return None
