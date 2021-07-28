from bblib.core.player_database_info import PlayerDatabaseInfo
from bblib.Util import update


class MoneyHandler:

    @staticmethod
    def add_money(player_info: PlayerDatabaseInfo, money_to_add: int) -> None:
        old_balance = player_info.money_amount
        update(["money_amount", old_balance + money_to_add], player_info.id)
        update(["total_gained", money_to_add], player_info.id)

    @staticmethod
    def remove_money(player_info: PlayerDatabaseInfo, money_to_remove: int) -> bool:
        old_balance = player_info.money_amount
        if old_balance - money_to_remove < 0:
            return False
        else:
            update(["money_amount", old_balance - money_to_remove], player_info.id)
            update(["total_lost", money_to_remove], player_info.id)
            return True

    @staticmethod
    def add_bank(player_info: PlayerDatabaseInfo, money_to_transfer: int) -> bool:
        old_money_balance = player_info.money_amount
        old_bank_balance = player_info.bank_amount
        if old_money_balance - money_to_transfer > 0:
            return False
        else:
            update(["money_amount", old_money_balance - money_to_transfer], player_info.id)
            update(["bank_amount", old_bank_balance + money_to_transfer], player_info.id)
            return True

    @staticmethod
    def remove_bank(player_info: PlayerDatabaseInfo, money_to_transfer: int) -> bool:
        old_money_balance = player_info.money_amount
        old_bank_balance = player_info.bank_amount
        if old_bank_balance - money_to_transfer > 0:
            return False
        else:
            update(["bank_amount", old_bank_balance - money_to_transfer], player_info.id)
            update(["money_amount", old_money_balance + money_to_transfer], player_info.id)
            return True

    @staticmethod
    def give_money(giver: PlayerDatabaseInfo, taker: PlayerDatabaseInfo, money_to_give: int) -> bool:
        if giver.money_amount - money_to_give < 0:
            return False
        else:
            update(["money_amount", money_to_give + taker.money_amount], taker.id)
            update(["money_amount", giver.money_amount - money_to_give], giver.id)
            return True

    @staticmethod
    def free_money(taker: PlayerDatabaseInfo, money_to_give: int):
        update(["money_amount", money_to_give + taker.money_amount], taker.id)
