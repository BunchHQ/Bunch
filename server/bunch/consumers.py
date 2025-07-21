import json
import logging
import time
import urllib.parse

from channels.db import database_sync_to_async
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
)
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from bunch.constants import WSMessageTypeClient, WSMessageTypeServer
from bunch.models import Bunch, Channel, Message, Reaction
from orchard.middleware import ClerkJWTAuthentication

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()

# active connections with timestamps
active_connections: dict[
    str, dict[str, float]
] = {}  # user_id -> {connection_id: timestamp}


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: User | None = None
        self._is_connected = False
        self.connection_id: str | None = None
        self.connection_time: float | None = None
        self.subscribed_channels = set()  # set of (bunch_id, channel_id)
        self.last_ping_time: float | None = None
        self.ping_interval: float = 30.0  # seconds
        self._connection_established = False

    async def connect(self):
        try:
            query_string = self.scope.get("query_string", b"").decode()
            query_params = urllib.parse.parse_qs(query_string)

            token = query_params.get("token", [None])[0]
            self.connection_id = query_params.get("connection_id", [None])[0]

            # is this is a keepalive connection
            self.is_keepalive = (
                query_params.get("keepalive", ["false"])[0] == "true"
            )
            if self.is_keepalive:
                logger.info(
                    f"Connection {self.connection_id} is a keepalive connection"
                )

            if not token:
                logger.warning("No token provided")
                await self.close(code=4001)
                return

            # accept the connection first to prevent timeouts
            await self.accept()
            self._connection_established = True
            logger.info(
                "WebSocket connection accepted, proceeding with authentication"
            )

            # Authenticate user
            try:
                auth = ClerkJWTAuthentication()
                request = HttpRequest()
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
                result = await database_sync_to_async(auth.authenticate)(
                    request  # pyright: ignore
                )
                if not result:
                    logger.warning("Authentication failed - no user returned")
                    await self.close(code=4002)
                    return

                user, _ = result

                self.user = user
                self.connection_time = time.time()

                # Track active connections, clean old connections
                await self._manage_active_connections(
                    self.user, str(self.connection_id), self.connection_time
                )

                logger.info(
                    f"User {self.user.username} authenticated successfully"
                )

            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                await self.close(code=4003)
                return

            self._is_connected = True
            logger.info(
                f"WebSocket connection fully established for user {self.user.username}"
            )
            # initial connection success message with more details
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "connection_established",
                        "connection_id": self.connection_id,
                        "is_keepalive": self.is_keepalive,
                        "server_time": time.time() * 1000,
                        "message": "Successfully connected. Use subscribe/unsubscribe messages to join channels",
                    }
                )
            )

        except Exception as e:
            logger.error(f"Unexpected error in connect: {str(e)}")
            if self._connection_established:
                await self.close(code=4000)

    async def _manage_active_connections(
        self, user: User, connection_id: str, connection_time: float
    ):
        self.last_ping_time = time.time()

        if str(user.id) in active_connections:
            old_connections = active_connections[str(user.id)]
            current_time = time.time()

            filtered_connections: dict[str, float] = {}
            # clean old connections (older than 10 minutes for keepalive,
            # 2 minutes for regular)
            for conn_id, timestamp in old_connections.items():
                # is this is a keepalive connection
                # for now just use the current connection's status
                is_keepalive_conn = (
                    conn_id == connection_id and self.is_keepalive
                )

                timeout = (
                    600 if is_keepalive_conn else 120
                )  # 10 minutes or 2 minutes

                if current_time - timestamp < timeout:
                    filtered_connections[conn_id] = timestamp

            logger.info(
                f"Active connections for user {user.id}: {len(filtered_connections)}"
            )

            # the holy check that prevents the damn disconnect/reconnect cycle
            # If this is a reconnection with the same connection_id,
            # don't close other connections
            if connection_id in filtered_connections:
                logger.info(
                    f"Reconnection with same ID {connection_id} for user {user.username}"
                )
                # Update the timestamp for this connection
                filtered_connections[connection_id] = connection_time
                active_connections[str(user.id)] = filtered_connections
            else:
                if not self.is_keepalive:
                    channel_layer = get_channel_layer()
                    assert channel_layer is not None
                    # Only close other connections if this is a new connection ID
                    # and not a keepalive connection
                    for old_conn_id in filtered_connections:
                        if old_conn_id != connection_id:
                            # send a close event to old connections
                            await channel_layer.group_send(
                                f"conn_{old_conn_id}",
                                {
                                    "type": "close_connection",
                                    "connection_id": old_conn_id,
                                },
                            )

                            logger.info(
                                f"Closed old connection {old_conn_id} for user {user.username}"
                            )

                    filtered_connections[connection_id] = connection_time
                    active_connections[str(user.id)] = filtered_connections
                else:
                    logger.info(
                        f"Keepalive connection {connection_id} - not closing other connections"
                    )
                    filtered_connections[connection_id] = connection_time
                    active_connections[str(user.id)] = filtered_connections
        else:
            active_connections[str(user.id)] = {
                str(connection_id): connection_time
            }

        connection_group = f"conn_{connection_id}"
        await self.channel_layer.group_add(connection_group, self.channel_name)

    async def disconnect(self, close_code):
        try:
            for bunch_id, channel_id in self.subscribed_channels:
                group_name = f"chat_{bunch_id}_{channel_id}"
                await self.channel_layer.group_discard(
                    group_name, self.channel_name
                )

            self.subscribed_channels.clear()

            if self.connection_id:
                connection_group = f"conn_{self.connection_id}"
                await self.channel_layer.group_discard(
                    connection_group, self.channel_name
                )

            # Remove from active connections if this is the current connection
            if self.user and str(self.user.id) in active_connections:
                if self.connection_id in active_connections[str(self.user.id)]:
                    del active_connections[str(self.user.id)][
                        self.connection_id
                    ]
                    if not active_connections[str(self.user.id)]:
                        del active_connections[str(self.user.id)]

            self._is_connected = False
            self._connection_established = False
            logger.info(f"WebSocket disconnected with code {close_code}")

        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def close_connection(self, event):
        # Only close the connection if explicitly requested and it's not a keepalive connection
        if (
            event.get("connection_id") == self.connection_id
            and not self.is_keepalive
        ):
            logger.info(
                f"Closing connection {self.connection_id} due to new connection"
            )
            await self.close(code=1000)
        elif (
            event.get("connection_id") == self.connection_id
            and self.is_keepalive
        ):
            logger.info(
                f"Ignoring close request for keepalive connection {self.connection_id}"
            )

    async def receive(self, text_data):
        try:
            assert self.user is not None

            data: dict[str, str] = json.loads(text_data)
            msg_type = data.get("type")

            logger.info(
                f"Received data: {msg_type}, from user: {self.user.username if self.user else 'Anonymous'}"
            )

            if msg_type == WSMessageTypeClient.PING:
                if self.user and str(self.user.id) in active_connections:
                    if (
                        self.connection_id
                        in active_connections[str(self.user.id)]
                    ):
                        active_connections[str(self.user.id)][
                            self.connection_id
                        ] = time.time()

                timestamp = data.get("timestamp", time.time() * 1000)
                #  pong!
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": WSMessageTypeServer.PONG,
                            "timestamp": timestamp,
                            "server_time": time.time() * 1000,
                        }
                    )
                )

            elif msg_type == WSMessageTypeClient.SUBSCRIBE:
                bunch_id = data.get("bunch_id")
                channel_id = data.get("channel_id")
                if not bunch_id or not channel_id:
                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": WSMessageTypeServer.ERROR,
                                "message": "Missing bunch_id or channel_id",
                            }
                        )
                    )
                    return

                has_access = await self.check_user_access(bunch_id, channel_id)
                if not has_access:
                    await self.send(
                        json.dumps(
                            {
                                "type": WSMessageTypeServer.ERROR,
                                "message": "Access denied to channel",
                            }
                        )
                    )
                    return

                group_name = f"chat_{bunch_id}_{channel_id}"
                if (bunch_id, channel_id) not in self.subscribed_channels:
                    await self.channel_layer.group_add(
                        group_name, self.channel_name
                    )
                    self.subscribed_channels.add((bunch_id, channel_id))
                else:
                    logger.warning(
                        f"{self.user.username} already subscribed to {group_name}"
                    )

                logger.info(f"{self.user.username} subscribed to {group_name}")

                await self.send(
                    json.dumps(
                        {
                            "type": WSMessageTypeServer.SUBSCRIBED,
                            "bunch_id": bunch_id,
                            "channel_id": channel_id,
                            "message": "Subscribed to channel",
                        }
                    )
                )

            elif msg_type == WSMessageTypeClient.UNSUBSCRIBE:
                bunch_id = data.get("bunch_id")
                channel_id = data.get("channel_id")
                if not bunch_id or not channel_id:
                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": WSMessageTypeServer.ERROR,
                                "message": "Missing bunch_id or channel_id",
                            }
                        )
                    )
                    return

                if (bunch_id, channel_id) in self.subscribed_channels:
                    group_name = f"chat_{bunch_id}_{channel_id}"
                    await self.channel_layer.group_discard(
                        group_name, self.channel_name
                    )
                    self.subscribed_channels.remove((bunch_id, channel_id))

                    logger.info(
                        f"{self.user.username} unsubscribed from {group_name}"
                    )

                    await self.channel_layer.group_send(
                        group_name,
                        {
                            "type": WSMessageTypeServer.UNSUBSCRIBED,
                            "bunch_id": bunch_id,
                            "channel_id": channel_id,
                            "message": "Unsubscribed from channel",
                        },
                    )

                else:
                    await self.send(
                        json.dumps(
                            {
                                "type": WSMessageTypeServer.ERROR,
                                "message": "Not subscribed to that channel",
                            }
                        )
                    )

            elif msg_type == WSMessageTypeClient.MESSAGE_NEW:
                bunch_id = data.get("bunch_id")
                channel_id = data.get("channel_id")
                content = data.get("content", "").strip()

                if not bunch_id or not channel_id:
                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": WSMessageTypeServer.ERROR,
                                "message": "Missing bunch_id or channel_id",
                            }
                        )
                    )
                    return

                if not content:
                    return

                if (bunch_id, channel_id) not in self.subscribed_channels:
                    await self.send(
                        json.dumps(
                            {
                                "type": WSMessageTypeServer.ERROR,
                                "message": "Not subscribed to channel",
                            }
                        )
                    )
                    return

                message_data = await database_sync_to_async(self._save_message)(
                    self.user, bunch_id, channel_id, content
                )
                logger.info(
                    f"Message created with ID: {message_data.get('id')}"
                )

                group_name = f"chat_{bunch_id}_{channel_id}"
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": WSMessageTypeServer.CHAT_MESSAGE,
                        "message": message_data,
                    },
                )

            elif msg_type in (
                WSMessageTypeClient.REACTION,
                WSMessageTypeClient.REACTION_TOGGLE,
            ):
                await self._handle_reaction(data)
                return

            else:
                logger.error(f"Invalid message type: {msg_type}")
                return

        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            raise e

    @database_sync_to_async
    def check_user_access(self, bunch_id, channel_id) -> bool:
        try:
            bunch = Bunch.objects.get(id=bunch_id)
            return bunch.members.filter(user=self.user).exists()
        except Exception:
            return False

    def _save_message(
        self, user: User, bunch_id: str, channel_id: str, content: str
    ):
        bunch = Bunch.objects.get(id=bunch_id)
        channel = Channel.objects.get(id=channel_id, bunch=bunch)
        member = bunch.members.get(user=user)

        message = Message.objects.create(
            content=content, author=member, channel=channel
        )

        # Eagerly load all related fields and prepare the message data
        return {
            "id": str(message.id),
            "channel": str(channel.id),
            "author": {
                "id": str(member.id),
                "bunch": str(bunch.id),
                "user": {
                    "id": str(member.user.id),
                    "username": member.user.username,
                },
                "role": member.role,
                "joined_at": member.joined_at.isoformat(),
            },
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "edit_count": message.edit_count,
            "deleted": message.deleted,
            "deleted_at": message.deleted_at.isoformat()
            if message.deleted_at
            else None,
        }

    async def _handle_reaction(self, data):
        """Handle reaction add/remove/toggle events."""
        assert self.user is not None

        try:
            action = data.get("action")  # "add", "remove", or None for toggle
            message_id = data.get("message_id")
            emoji = data.get("emoji")
            bunch_id = data.get("bunch_id")
            channel_id = data.get("channel_id")
            group_name = f"chat_{bunch_id}_{channel_id}"

            if not all([message_id, emoji, bunch_id, channel_id]):
                logger.warning("Invalid reaction data received")
                return

            has_access = await self.check_user_access(bunch_id, channel_id)
            if not has_access:
                logger.warning(
                    f"User {self.user.username} denied reaction access to bunch {bunch_id} channel {channel_id}"
                )
                return

            # reaction exists -> add/remove accordingly
            if (
                data.get("type") == WSMessageTypeClient.REACTION_TOGGLE
                or not action
            ):

                def check_existing_reaction():
                    return Reaction.objects.filter(
                        message_id=message_id,
                        user=self.user,
                        emoji=emoji,
                    ).first()

                existing_reaction = await database_sync_to_async(
                    check_existing_reaction
                )()

                if existing_reaction:
                    reaction_data = await database_sync_to_async(
                        self._remove_reaction
                    )(self.user, bunch_id, message_id, emoji)

                    if reaction_data:
                        await self.channel_layer.group_send(
                            group_name,
                            {
                                "type": WSMessageTypeServer.REACTION_REMOVED,
                                "reaction": reaction_data,
                            },
                        )
                else:
                    reaction_data = await database_sync_to_async(
                        self._add_reaction
                    )(self.user, bunch_id, message_id, emoji)

                    if reaction_data:
                        # Broadcast
                        await self.channel_layer.group_send(
                            group_name,
                            {
                                "type": WSMessageTypeServer.REACTION_ADDED,
                                "reaction": reaction_data,
                            },
                        )
                return

            # Handle explicit add/remove actions
            if action == "add":
                reaction_data = await database_sync_to_async(
                    self._add_reaction
                )(self.user, bunch_id, message_id, emoji)

                if reaction_data:
                    # Broadcast reaction add event
                    await self.channel_layer.group_send(
                        group_name,
                        {
                            "type": WSMessageTypeServer.REACTION_ADDED,
                            "reaction": reaction_data,
                        },
                    )

            elif action == "remove":
                reaction_data = await database_sync_to_async(
                    self._remove_reaction
                )(self.user, bunch_id, message_id, emoji)

                if reaction_data:
                    # Broadcast reaction remove event
                    await self.channel_layer.group_send(
                        group_name,
                        {
                            "type": WSMessageTypeServer.REACTION_REMOVED,
                            "reaction": reaction_data,
                        },
                    )

        except Exception as e:
            logger.error(f"Error handling reaction: {str(e)}")

    def _add_reaction(
        self, user: User, bunch_id: str, message_id: str, emoji: str
    ):
        """Add a reaction to a message."""
        try:
            bunch = Bunch.objects.get(id=bunch_id)
            message = Message.objects.get(id=message_id, channel__bunch=bunch)

            # Check if user is a member of the bunch
            if not bunch.members.filter(user=user).exists():
                logger.warning(
                    f"User {user.username} not a member of bunch {bunch.name}"
                )
                return None

            # Check if reaction already exists
            if Reaction.objects.filter(
                message=message, user=user, emoji=emoji
            ).exists():
                logger.info(
                    f"Reaction already exists: {emoji} by {user.username}"
                )
                return None

            # Create the reaction
            reaction = Reaction.objects.create(
                message=message, user=user, emoji=emoji
            )

            logger.info(
                f"Reaction added: {emoji} by {user.username} to message {message_id}"
            )

            return {
                "id": str(reaction.id),
                "message_id": str(message.id),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                },
                "emoji": reaction.emoji,
                "created_at": reaction.created_at.isoformat(),
            }

        except (
            Bunch.DoesNotExist,
            Message.DoesNotExist,
        ) as e:
            logger.error(f"Error adding reaction: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error adding reaction: {str(e)}")
            return None

    def _remove_reaction(
        self, user: User, bunch_id: str, message_id: str, emoji: str
    ):
        """Remove a reaction from a message."""
        try:
            bunch = Bunch.objects.get(id=bunch_id)
            message = Message.objects.get(id=message_id, channel__bunch=bunch)

            # Find the reaction
            reaction = Reaction.objects.filter(
                message=message, user=user, emoji=emoji
            ).first()

            if not reaction:
                logger.warning(
                    f"Reaction not found: {emoji} by {user.username}"
                )
                return None

            reaction_data = {
                "id": str(reaction.id),
                "message_id": str(message.id),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                },
                "emoji": reaction.emoji,
                "created_at": reaction.created_at.isoformat(),
            }

            reaction.delete()
            logger.info(
                f"Reaction removed: {emoji} by {user.username} from message {message_id}"
            )

            return reaction_data

        except (
            Bunch.DoesNotExist,
            Message.DoesNotExist,
        ) as e:
            logger.error(f"Error removing reaction: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error removing reaction: {str(e)}")
            return None

    async def reaction_added(self, event):
        """Send reaction added event to WebSocket."""
        if not self._is_connected:
            logger.warning("Received reaction_added while not connected")
            return

        try:
            reaction = event["reaction"]
            logger.info(f"Sending reaction added to client: {reaction['id']}")
            await self.send(
                text_data=json.dumps(
                    {
                        "type": WSMessageTypeServer.REACTION_NEW,
                        "reaction": reaction,
                    }
                )
            )
        except Exception as e:
            logger.error(f"Error in reaction_added: {str(e)}")

    async def reaction_removed(self, event):
        """Send reaction removed event to WebSocket."""
        if not self._is_connected:
            logger.warning("Received reaction_removed while not connected")
            return

        try:
            reaction = event["reaction"]
            logger.info(f"Sending reaction removed to client: {reaction['id']}")
            await self.send(
                text_data=json.dumps(
                    {
                        "type": WSMessageTypeServer.REACTION_DELETE,
                        "reaction": reaction,
                    }
                )
            )
        except Exception as e:
            logger.error(f"Error in reaction_removed: {str(e)}")

    async def chat_message(self, event):
        if not self._is_connected:
            logger.warning("Received chat_message while not connected")
            return

        try:
            message = event["message"]
            logger.info(f"Sending message to client: {message['id']}")
            await self.send(
                text_data=json.dumps(
                    {
                        "type": WSMessageTypeServer.CHAT_MESSAGE,
                        "message": message,
                    }
                )
            )
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}")
