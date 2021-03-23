def get_member_str(member) -> str:
    return member.name if member.nick is None else member.nick


def get_member_object(ctx, member_id: str):
    member_object = ctx.guild.get_member(int(member_id))
    return member_object


async def message_channel(ctx, incoming_message=None, embed=None) -> None:
    if not embed:
        await ctx.message.channel.send(incoming_message)
    else:
        await ctx.message.channel.send(embed=embed)
