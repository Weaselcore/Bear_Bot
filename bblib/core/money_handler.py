import datetime

from bblib.core.player_database_info import PlayerDatabaseInfo
from bblib.Util import update, update_money_amount, update_total_gained, update_last_redeemed, update_total_lost, \
    update_bank_amount, update_last_bank_datetime


class MoneyHandler:

    @staticmethod
    def redeem(player_info: PlayerDatabaseInfo, money_to_add: int) -> None:
        old_balance = player_info.money_amount
        update_money_amount(player_info.id, old_balance + money_to_add)
        update_total_gained(player_info.id, money_to_add + player_info.total_gained)
        update_last_redeemed(player_info.id, str(datetime.datetime.now()))

    @staticmethod
    def add_money(player_info: PlayerDatabaseInfo, money_to_add: int) -> None:
        update_money_amount(player_info.id, player_info.money_amount + money_to_add)
        update_total_gained(player_info.id, money_to_add + player_info.total_gained)

    @staticmethod
    def remove_money(player_info: PlayerDatabaseInfo, money_to_remove: int) -> bool:
        old_balance = player_info.money_amount
        if old_balance - money_to_remove < 0:
            return False
        else:
            update_money_amount(player_info.id, old_balance - money_to_remove)
            update_total_lost(player_info.id, money_to_remove + player_info.total_lost)
            return True

    @staticmethod
    def add_bank(player_info: PlayerDatabaseInfo, money_to_transfer: int) -> bool:

        if player_info.money_amount - money_to_transfer < 0:
            return False
        else:
            update_money_amount(player_info.id, player_info.money_amount - money_to_transfer)
            update_bank_amount(player_info.id, player_info.bank_amount + money_to_transfer)
            update_last_bank_datetime(player_info.id, str(datetime.datetime.now()))
            return True

    @staticmethod
    def remove_bank(player_info: PlayerDatabaseInfo, money_to_transfer: int) -> bool:
        if player_info.bank_amount - money_to_transfer < 0:
            return False
        else:
            update_money_amount(player_info.id, player_info.money_amount + money_to_transfer)
            update_bank_amount(player_info.id, player_info.bank_amount - money_to_transfer)
            return True

    @staticmethod
    def give_money(giver: PlayerDatabaseInfo, taker: PlayerDatabaseInfo, money_to_give: int):
        if giver.money_amount - money_to_give < 0:
            money_to_give = giver.money_amount

        update_money_amount(taker.id, money_to_give + taker.money_amount)
        update_total_gained(taker.id, money_to_give + taker.total_gained)

        update_money_amount(giver.id, giver.money_amount - money_to_give)
        update_total_lost(giver.id, money_to_give + giver.total_lost)

    @staticmethod
    def free_money(player_info: PlayerDatabaseInfo, money_to_give: int):
        update_money_amount(player_info.id, money_to_give + player_info.money_amount)
