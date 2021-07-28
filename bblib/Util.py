from random import choice
from typing import Union

from DatabaseWrapper import DatabaseWrapper


def get_member_str(member) -> Union[str, None]:
    if member:
        return member.name if member.nick is None else member.nick
    else:
        return None


def get_member_object(ctx, member_id: int):
    member_object = ctx.guild.get_member(member_id)
    return member_object


def get_number_arg(ctx) -> Union[int, None]:
    value_to_return = None
    list_of_args = ctx.message.content.split(' ')
    if len(list_of_args) > 1:
        try:
            value_to_return = int(list_of_args[1])
            return value_to_return
        except ValueError as e:
            print(e)
    return value_to_return


async def message_channel(ctx, incoming_message=None, embed=None) -> None:
    if not embed:
        await ctx.message.channel.send(incoming_message)
    else:
        await ctx.message.channel.send(embed=embed)


def member_create(ctx):
    """
    Is a predicate function for the @command.check decorator.
    This ensures that the member that's being queried will have a row available.
    :param ctx:
    :return True: Will always be the case.
    """
    with DatabaseWrapper() as database:
        members_to_check = [ctx.message.author.id]
        members_to_check.extend(ctx.message.raw_mentions)
        for member in members_to_check:  # Deposit amount.
            cursor = database.execute("SELECT _id FROM gambler_stat WHERE _id=?", (member,))
            result = cursor.fetchall()
            if not result:
                database.execute("INSERT INTO gambler_stat (_id, money_amount) values(?, 0);", (member,))
    return True


def fifty() -> bool:
    return choice([True, False])


def get_single_value(column_name: str, table_name: str, filter_name: str, filter_str: int):
    with DatabaseWrapper() as database:
        cursor = database.execute("SELECT FROM ? WHERE ?=?", (column_name, table_name, filter_name, filter_str,))
        result = cursor.fetchall()[0][0]
        return result


def get_row(table_name: str, filter_name: str, filter_str: int):
    with DatabaseWrapper() as database:
        cursor = database.execute("SELECT * FROM ?WHERE (?)=?", (table_name, filter_name, filter_str,))
        result = cursor.fetchall()
        return result


def get_money(member_id) -> int:
    money = get_single_value('money_amount', 'gambler_stat', '_id', member_id)
    return money


def get_bank(member_id) -> int:
    bank = get_single_value('bank_amount', 'gambler_stat', '_id', member_id)
    return bank


def get_last_redeemed(member_id):
    last_redeemed_time = get_single_value('last_redeemed', 'gambler_stat', '_id', member_id)
    return last_redeemed_time


def get_total_gained(member_id) -> int:
    total_gained = get_single_value('total_gained', 'gambler_stat', '_id', member_id)
    return total_gained


def get_total_lost(member_id) -> int:
    total_lost = get_single_value('total_lost', 'gambler_stat', '_id', member_id)
    return total_lost


def get_stolen_id(member_id):
    stolen_name = get_single_value('last_stolen_id', 'gambler_stat', '_id', member_id)
    return stolen_name


def get_stolen_time(member_id):
    stolen_time = get_single_value('last_stolen_datetime', 'gambler_stat', '_id', member_id)
    return stolen_time


def get_last_bank_time(member_id):
    last_bank_time = get_single_value('last_bank_datetime', 'gambler_stat', '_id', member_id)
    return last_bank_time


def update(list_to_change: list, member_id: int):
    # nickname, money_amount, last_stolen_id, last_redeemed, last_stolen_datetime, total_gained, total_lost
    with DatabaseWrapper() as database:
        database.execute(
            'UPDATE gambler_stat SET ? = ? WHERE _id = ?;', (list_to_change[0], list_to_change[1], member_id,)
        )
