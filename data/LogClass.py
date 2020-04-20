import mongoengine


class Log(mongoengine.Document):

    datetime = mongoengine.DateTimeField(required=True)
    member_id = mongoengine.StringField(required=True)
    member_name = mongoengine.StringField(required=True)
    member_display_name = mongoengine.StringField(required=True)

    client = mongoengine.BooleanField(required=False)
