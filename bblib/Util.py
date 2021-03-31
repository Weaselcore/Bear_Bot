from typing import Union


def get_member_str(member) -> str:
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
