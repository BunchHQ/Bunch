from enum import StrEnum


# must be kept in sync with apps/web/bunch/lib/types.ts
class WSMessageTypeClient(StrEnum):
    """
    Message types that websocket client sends, server receives.
    """

    PING = "ping"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    # message
    MESSAGE_NEW = "message.new"
    MESSAGE_UPDATE = "message.update"
    MESSAGE_DELETE = "message.delete"
    # reactions
    REACTION = "reaction"
    REACTION_NEW = "reaction.new"
    REACTION_DELETE = "reaction.delete"
    REACTION_TOGGLE = "reaction.toggle"


class WSMessageTypeServer(StrEnum):
    """
    Message types that websocket server sends, client receives.
    """

    PONG = "pong"
    ERROR = "error"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    CHAT_MESSAGE = "chat.message"
    REACTION_NEW = "reaction.new"
    REACTION_DELETE = "reaction.delete"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
