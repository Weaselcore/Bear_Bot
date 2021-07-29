from typing import Union

from bblib.Util import get_row
from bblib.core.player_database_info import PlayerDatabaseInfo


class PlayerInfoFactory:

    @staticmethod
    def generate(member_id: int) -> Union[None, PlayerDatabaseInfo]:
        result = get_row(member_id)
        if result is not None:
            player_info = PlayerDatabaseInfo(id=result[0],
                                             nickname=result[1],
                                             money_amount=result[2],
                                             bank_amount=result[3],
                                             last_stolen_id=result[4],
                                             last_redeemed=result[5],
                                             last_bank_time=result[6],
                                             last_stolen_time=result[7],
                                             total_gained=result[8],
                                             total_lost=result[9])
            return player_info
        else:
            return None
