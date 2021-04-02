import datetime
from random import choice
from typing import Union

import discord

from DatabaseWrapper import DatabaseWrapper


def get_member_str(member: discord.member) -> str:
    return member.name if member.nick is None else member.nick


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
            cursor = database.execute(f"SELECT _id FROM gambler_stat WHERE _id={member}")
            result = cursor.fetchall()
            if not result:
                database.execute(f"""INSERT INTO gambler_stat (_id, money_amount) values({member}, 0);""")
    return True


def fifty() -> bool:
    return choice([True, False])


def get_single_value(column_name: str, table_name: str, filter_name: str, filter_str: int):
    with DatabaseWrapper() as database:
        cursor = database.execute(f"SELECT {column_name} FROM {table_name} WHERE ({filter_name})={filter_str}")
        result = cursor.fetchall()[0][0]
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


def update(list_to_change: list, member_id):
    # nickname, money_amount, last_stolen_id, last_redeemed, last_stolen_datetime, total_gained, total_lost
    with DatabaseWrapper() as database:
        values = list(zip(*list_to_change))
        database.execute(f'''UPDATE gambler_stat SET {values[0]} = {values[1]} WHERE _id = {member_id};''')


def update_money(member, money_to_update, add_wallet=True, banking=False, redeem=False):
    wallet_amount = get_money(member.id)
    bank_amount = get_bank(member.id)
    total_gained = get_total_gained(member.id)
    total_lost = get_total_lost(member.id)

    if banking:
        if add_wallet:
            wallet_amount = wallet_amount + money_to_update
            bank_amount = bank_amount - money_to_update
        else:
            wallet_amount = wallet_amount - money_to_update
            bank_amount = bank_amount + money_to_update
    elif not banking:
        if add_wallet:
            total_gained = total_gained + money_to_update
            wallet_amount = wallet_amount + money_to_update
        else:
            total_lost = total_lost + money_to_update
            wallet_amount = wallet_amount - money_to_update
            # TODO Dirty hack, implement better validation with discord py testing library.
            if wallet_amount < 0:
                wallet_amount = 0

    data_tuple = [('nickname', get_member_str(member)), ('money_amount', wallet_amount),
                  ('total_gained', total_gained), ('total_lost', total_lost), ('bank_amount', bank_amount)]

    if redeem:
        data_tuple.append(('last_redeemed', str(datetime.datetime.utcnow())))
    if banking and not add_wallet:
        data_tuple.append(('last_bank_datetime', str(datetime.datetime.utcnow())))

    update(data_tuple, member_id=member.id)
