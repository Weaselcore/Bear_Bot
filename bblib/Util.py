import datetime
from typing import Union

import discord

from DatabaseWrapper import DatabaseWrapper
from cogs.gambler import get_money, get_bank, get_total_gained, get_total_lost, update


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


def update_money(member, money_to_update, add_wallet=True, banking=False, redeem=False):
    wallet_amount, bank_amount = get_money(member.id), get_bank(member.id)
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

    data_tuple = [('nickname', get_member_str(member)), ('money_amount', wallet_amount),
                  ('total_gained', total_gained), ('total_lost', total_lost), ('bank_amount', bank_amount)]

    if redeem:
        data_tuple.append(('last_redeemed', str(datetime.datetime.utcnow())))
    if banking and not add_wallet:
        data_tuple.append(('last_bank_datetime', str(datetime.datetime.utcnow())))

    update(data_tuple, member_id=member.id)