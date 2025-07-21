from enum import StrEnum


class WSMessageTypeClient(StrEnum):
    """
    Message types that websocket client sends, server receives.
    """

    PING = "ping"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SEND_MESSAGE = "send_message"
    REACTION = "reaction"
    REACTION_TOGGLE = "reaction.toggle"


class WSMessageTypeServer(StrEnum):
    """
    Message types that websocket server sends, client receives.
    """

    PONG = "pong"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    ERROR = "error"
    CHAT_MESSAGE_SENT = "chat.message"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    # Why ???
    CHAT_MESSAGE = "chat.message"
    REACTION_NEW = "reaction.new"
    REACTION_DELETE = "reaction.delete"
