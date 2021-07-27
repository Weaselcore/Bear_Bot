from typing import Union

from DatabaseWrapper import DatabaseWrapper
from bblib.core.player_database_info import PlayerDatabaseInfo


class PlayerInfoFactory:

    @staticmethod
    def generate(member_id: int) -> Union[None, PlayerDatabaseInfo]:
        with DatabaseWrapper() as database:
            if database:
                result = database.execute(f"SELECT * FROM 'GAMBLER_STAT' WHERE _id = {member_id}")
                for rows in result:
                    player_info = PlayerDatabaseInfo(id=rows[0],
                                                     nickname=rows[1],
                                                     money_amount=rows[2],
                                                     bank_amount=rows[3],
                                                     last_stolen_id=rows[4],
                                                     last_redeemed=rows[5],
                                                     last_bank_time=rows[6],
                                                     last_stolen_time=rows[7],
                                                     total_gained=rows[8],
                                                     total_lost=rows[9])
                if player_info:
                    return player_info
                else:
                    return None




