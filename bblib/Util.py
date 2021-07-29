from random import choice
from typing import Union

from DatabaseWrapper import DatabaseWrapper
from bblib.core.database_statement import SqlStatement


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

    members_to_check = [ctx.message.author.id]
    members_to_check.extend(ctx.message.raw_mentions)
    for member in members_to_check:  # Deposit amount.
        result = get(SqlStatement.GET_ID, member)
        if not result:
            insert(SqlStatement.INSERT_ID, (member,))
    return True


def fifty() -> bool:
    return choice([True, False])


def check_tables(name: str):
    return get(SqlStatement.CHECK_TABLES, name)


def get_nickname(member_id: int):
    return get(SqlStatement.GET_NICKNAME, member_id)


def get_money(member_id: int) -> int:
    return get(SqlStatement.GET_MONEY, member_id)


def get_bank(member_id: int) -> int:
    return get(SqlStatement.GET_BANK, member_id)


def get_last_redeemed(member_id: int):
    return get(SqlStatement.GET_LAST_REDEEMED, member_id)


def get_total_gained(member_id: int) -> int:
    return get(SqlStatement.GET_TOTAL_GAINED, member_id)


def get_total_lost(member_id: int) -> int:
    return get(SqlStatement.GET_TOTAL_LOST, member_id)


def get_stolen_id(member_id: int):
    return get(SqlStatement.GET_LAST_STOLEN_ID, member_id)


def get_stolen_time(member_id: int):
    return get(SqlStatement.GET_LAST_STOLEN_DATETIME, member_id)


def get_last_bank_time(member_id):
    return get(SqlStatement.GET_LAST_BANK_DATETIME, member_id)


def get_leader(result_limit: int):
    with DatabaseWrapper() as database:
        cursor = database.execute(SqlStatement.GET_LEADER, (result_limit,))
        result = cursor.fetchall()
        return result


def update_nickname(member_id: int, new_nickname: str):
    update(SqlStatement.UPDATE_NICKNAME, new_nickname, member_id)


def update_money_amount(member_id: int, money_to_add: int):
    update(SqlStatement.UPDATE_MONEY, money_to_add, member_id)


def update_bank_amount(member_id: int, bank_to_add: int):
    update(SqlStatement.UPDATE_BANK, bank_to_add, member_id)


def update_last_stolen_id(member_id: int, victim_id: int):
    update(SqlStatement.UPDATE_LAST_STOLEN_ID, victim_id, member_id)


def update_last_redeemed(member_id: int, new_redeemed_datetime):
    update(SqlStatement.UPDATE_LAST_REDEEMED, new_redeemed_datetime, member_id)


def update_last_bank_datetime(member_id: int, new_bank_datetime):
    update(SqlStatement.UPDATE_LAST_BANK_DATETIME, new_bank_datetime, member_id)


def update_last_stolen_datetime(member_id: int, new_stolen_datetime):
    update(SqlStatement.UPDATE_LAST_STOLEN_DATETIME, new_stolen_datetime, member_id)


def update_total_gained(member_id: int, new_total_gained: int):
    update(SqlStatement.UPDATE_TOTAL_GAINED, new_total_gained, member_id)


def update_total_lost(member_id: int, new_total_lost: int):
    update(SqlStatement.UPDATE_TOTAL_LOST, new_total_lost, member_id)


def insert_id(member_id: int):
    insert(SqlStatement.INSERT_ID, (member_id,))


def insert_guild(guild_id: int, guild_name: str, guild_creation_datetime):
    insert(SqlStatement.INSERT_GUILD, (guild_id, guild_name, guild_creation_datetime,))


def get_row(member_id: int):
    with DatabaseWrapper() as database:
        cursor = database.execute(SqlStatement.GET_ROW, (member_id,))
        result = cursor.fetchone()
        return result


def get(statement, value: Union[str, int]):
    with DatabaseWrapper() as database:
        cursor = database.execute(statement, (value,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


def update(statement: SqlStatement, values, member_id: int):
    # nickname, money_amount, last_stolen_id, last_redeemed, last_stolen_datetime, total_gained, total_lost
    with DatabaseWrapper() as database:
        database.execute(statement, (values, member_id,))


def insert(statement: SqlStatement, values: tuple):
    with DatabaseWrapper() as database:
        database.execute(statement, values)
