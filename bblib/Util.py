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
