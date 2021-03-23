def get_member_str(member) -> str:
    return member.name if member.nick is None else member.nick


def get_member_object(ctx, member_id: str):
    member_object = ctx.guild.get_member(int(member_id))
    return member_object
