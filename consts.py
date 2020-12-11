import httpx


group_types = ("group", "supergroup")

http = httpx.AsyncClient(http2=True)


class Permissions:
    can_be_edited = "can_be_edited"
    delete_messages = "can_delete_messages"
    restrict_members = "can_restrict_members"
    promote_members = "can_promote_members"
    change_info = "can_change_info"
    invite_users = "can_invite_users"
    pin_messages = "can_pin_messages"
