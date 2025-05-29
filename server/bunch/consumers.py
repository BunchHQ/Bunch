import json
import logging
import time
import urllib.parse
from typing import Dict, Optional

from bunch.models import Bunch, Channel, Message, Reaction
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from orchard.middleware import ClerkJWTAuthentication

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()

# active connections with timestamps
active_connections: Dict[
    str, Dict[str, float]
] = {}  # user_id -> {connection_id: timestamp}


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bunch_id: Optional[str] = None
        self.channel_id: Optional[str] = None
        self.room_group_name: Optional[str] = None
        self.user: Optional[User] = None
        self._is_connected = False
        self.connection_id: Optional[str] = None
        self.connection_time: Optional[float] = None
        self.last_ping_time: Optional[float] = None
        self.ping_interval: float = 30.0  # seconds
        self._connection_established = False

    async def connect(self):
        try:
            self.bunch_id = self.scope["url_route"][
                "kwargs"
            ]["bunch_id"]
            self.channel_id = self.scope["url_route"][
                "kwargs"
            ]["channel_id"]
            self.room_group_name = (
                f"chat_{self.bunch_id}_{self.channel_id}"
            )

            query_string = self.scope.get(
                "query_string", b""
            ).decode()
            query_params = urllib.parse.parse_qs(
                query_string
            )

            token = query_params.get("token", [None])[0]
            self.connection_id = query_params.get(
                "connection_id", [None]
            )[0]

            # is this is a keepalive connection
            self.is_keepalive = (
                query_params.get("keepalive", ["false"])[0]
                == "true"
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
                request.META["HTTP_AUTHORIZATION"] = (
                    f"Bearer {token}"
                )
                user, _ = await database_sync_to_async(
                    auth.authenticate
                )(request)

                if not user:
                    logger.warning(
                        "Authentication failed - no user returned"
                    )
                    await self.close(code=4002)
                    return

                self.user = user
                self.connection_time = time.time()
                self.last_ping_time = time.time()
                logger.info(
                    f"User {user.username} authenticated successfully"
                )

                if str(user.id) in active_connections:
                    old_connections = active_connections[
                        str(user.id)
                    ]
                    current_time = time.time()

                    existing_connections = (
                        active_connections[str(user.id)]
                    )

                    # clean old connections (older than 10 minutes for keepalive,
                    # 2 minutes for regular)
                    old_connections = {}
                    for (
                        conn_id,
                        timestamp,
                    ) in existing_connections.items():
                        # is this is a keepalive connection
                        # for now just use the current connection's status
                        is_keepalive_conn = (
                            conn_id == self.connection_id
                            and self.is_keepalive
                        )

                        timeout = (
                            600
                            if is_keepalive_conn
                            else 120
                        )  # 10 minutes or 2 minutes

                        if (
                            current_time - timestamp
                            < timeout
                        ):
                            old_connections[conn_id] = (
                                timestamp
                            )

                    logger.info(
                        f"Active connections for user {user.id}: {len(old_connections)}"
                    )

                    # the holy check that prevents the damn disconnect/reconnect cycle
                    # If this is a reconnection with the same connection_id,
                    # don't close other connections
                    if (
                        self.connection_id
                        in old_connections
                    ):
                        logger.info(
                            f"Reconnection with same ID {self.connection_id} for user {user.username}"
                        )
                        # Update the timestamp for this connection
                        old_connections[
                            self.connection_id
                        ] = self.connection_time
                        active_connections[str(user.id)] = (
                            old_connections
                        )
                        # Skip closing other connections

                    if self.is_keepalive:
                        logger.info(
                            f"This is a keepalive connection with ID {self.connection_id}"
                        )
                    else:
                        # Don't close any connections if this is a keepalive connection
                        if not self.is_keepalive:
                            # Only close other connections if this is a new connection ID
                            # and not a keepalive connection
                            for (
                                old_conn_id
                            ) in old_connections:
                                if (
                                    old_conn_id
                                    != self.connection_id
                                ):
                                    channel_layer = (
                                        get_channel_layer()
                                    )
                                    await channel_layer.group_send(
                                        f"chat_{self.bunch_id}_{self.channel_id}",
                                        {
                                            "type": "close_connection",
                                            "connection_id": old_conn_id,
                                        },
                                    )
                                    logger.info(
                                        f"Closed old connection {old_conn_id} for user {user.username}"
                                    )
                        else:
                            logger.info(
                                f"Keepalive connection {self.connection_id} - not closing other connections"
                            )

                        if (
                            self.connection_id
                            not in old_connections
                        ):
                            active_connections[
                                str(user.id)
                            ] = {
                                self.connection_id: self.connection_time
                            }
                else:
                    active_connections[str(user.id)] = {
                        self.connection_id: self.connection_time
                    }

            except Exception as e:
                logger.error(
                    f"Authentication error: {str(e)}"
                )
                await self.close(code=4003)
                return

            # check user has access to the channel
            try:
                bunch = await database_sync_to_async(
                    Bunch.objects.get
                )(id=self.bunch_id)
                channel = await database_sync_to_async(
                    Channel.objects.get
                )(id=self.channel_id, bunch=bunch)

                # check user is a member of the bunch
                is_member = await database_sync_to_async(
                    lambda: bunch.members.filter(
                        user=self.user
                    ).exists()
                )()
                if not is_member:
                    logger.warning(
                        f"User {self.user.username} is not a member of bunch {bunch.name}"
                    )
                    await self.close(code=4005)
                    return

                logger.info(
                    f"User {self.user.username} connected to channel {channel.name}"
                )

                # join room group
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )
                self._is_connected = True

                if self.is_keepalive:
                    # Create a special group name for this connection ID to manage multiple connections
                    connection_group = (
                        f"connection_{self.connection_id}"
                    )
                    await self.channel_layer.group_add(
                        connection_group, self.channel_name
                    )

                logger.info(
                    f"WebSocket connection fully established for user {self.user.username}"
                )

                # initial connection success message with more details
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "connection_established",
                            "message": "Successfully connected to channel",
                            "connection_id": self.connection_id,
                            "is_keepalive": self.is_keepalive,
                            "server_time": time.time()
                            * 1000,
                            "channel": {
                                "id": str(channel.id),
                                "name": channel.name,
                                "bunch_id": str(bunch.id),
                                "bunch_name": bunch.name,
                            },
                        }
                    )
                )

            except ObjectDoesNotExist:
                logger.warning(
                    f"Channel or bunch not found: bunch_id={self.bunch_id}, channel_id={self.channel_id}"
                )
                await self.close(code=4004)
                return
            except Exception as e:
                logger.error(
                    f"Channel access error: {str(e)}"
                )
                await self.close(code=4004)
                return

        except Exception as e:
            logger.error(
                f"Unexpected error in connect: {str(e)}"
            )
            if self._connection_established:
                await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            if self._is_connected and hasattr(
                self, "room_group_name"
            ):
                # Leave room group
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )

                # If this was a keepalive connection, leave the connection group
                if (
                    hasattr(self, "is_keepalive")
                    and self.is_keepalive
                    and hasattr(self, "connection_id")
                ):
                    connection_group = (
                        f"connection_{self.connection_id}"
                    )
                    await self.channel_layer.group_discard(
                        connection_group, self.channel_name
                    )

            # Remove from active connections if this is the current connection
            if (
                self.user
                and str(self.user.id) in active_connections
            ):
                if (
                    self.connection_id
                    in active_connections[str(self.user.id)]
                ):
                    del active_connections[
                        str(self.user.id)
                    ][self.connection_id]
                    if not active_connections[
                        str(self.user.id)
                    ]:
                        del active_connections[
                            str(self.user.id)
                        ]

            self._is_connected = False
            self._connection_established = False
            logger.info(
                f"WebSocket disconnected with code {close_code}"
            )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def close_connection(self, event):
        # Only close the connection if explicitly requested and it's not a keepalive connection
        if event[
            "connection_id"
        ] == self.connection_id and not getattr(
            self, "is_keepalive", False
        ):
            logger.info(
                f"Closing connection {self.connection_id} due to new connection"
            )
            await self.close(code=1000)
        elif event[
            "connection_id"
        ] == self.connection_id and getattr(
            self, "is_keepalive", False
        ):            logger.info(
                f"Ignoring close request for keepalive connection {self.connection_id}"
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            logger.info(
                f"Received data: {data.get('type')}, from user: {self.user.username if self.user else 'Anonymous'}"
            )

            # ping!
            if data.get("type") == "ping":
                if (
                    self.user
                    and str(self.user.id)
                    in active_connections
                ):
                    if (
                        self.connection_id
                        in active_connections[
                            str(self.user.id)
                        ]
                    ):
                        active_connections[
                            str(self.user.id)
                        ][self.connection_id] = time.time()

                timestamp = data.get(
                    "timestamp", time.time() * 1000
                )
                #  pong!
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "pong",
                            "timestamp": timestamp,
                            "server_time": time.time()
                            * 1000,
                        }
                    )
                )
                return            
            
            # Handle reaction events
            if data.get("type") == "reaction" or data.get("type") == "reaction.toggle":
                await self._handle_reaction(data)
                return

            # Handle regular chat messages
            content = data.get("content")
            if not content or not content.strip():
                return

            # Save message and get message data in sync context
            message_data = await database_sync_to_async(
                self._save_message
            )(self.user, content.strip())
            logger.info(
                f"Message created with ID: {message_data['id']}"
            )
            logger.info(
                f"Message saved: {message_data['id']} from {message_data['author']['user']['username']}"
            )

            # broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message_data,
                },
            )

        except Exception as e:
            raise e
            logger.error(f"Error in receive: {str(e)}")

    def _save_message(self, user, content):
        bunch = Bunch.objects.get(id=self.bunch_id)
        channel = Channel.objects.get(
            id=self.channel_id, bunch=bunch
        )
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
        try:
            action = data.get("action")  # "add", "remove", or None for toggle
            message_id = data.get("message_id")
            emoji = data.get("emoji")

            if not all([message_id, emoji]):
                logger.warning("Invalid reaction data received")
                return            
            
            # reaction exists -> add/remove accordingly
            if data.get("type") == "reaction.toggle" or not action:
                def check_existing_reaction():
                    return Reaction.objects.filter(
                        message_id=message_id,
                        user=self.user,
                        emoji=emoji
                    ).first()
                
                existing_reaction = await database_sync_to_async(check_existing_reaction)()
                
                if existing_reaction:
                    reaction_data = await database_sync_to_async(
                        self._remove_reaction
                    )(self.user, message_id, emoji)
                    
                    if reaction_data:
                        # Broadcast 
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "reaction_removed",
                                "reaction": reaction_data,
                            },
                        )
                else:
                    reaction_data = await database_sync_to_async(
                        self._add_reaction
                    )(self.user, message_id, emoji)
                    
                    if reaction_data:
                        # Broadcast
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "reaction_added",
                                "reaction": reaction_data,
                            },
                        )
                return

            # Handle explicit add/remove actions
            if action == "add":
                reaction_data = await database_sync_to_async(
                    self._add_reaction
                )(self.user, message_id, emoji)
                
                if reaction_data:
                    # Broadcast reaction add event
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "reaction_added",
                            "reaction": reaction_data,
                        },
                    )
            
            elif action == "remove":
                reaction_data = await database_sync_to_async(
                    self._remove_reaction
                )(self.user, message_id, emoji)
                
                if reaction_data:
                    # Broadcast reaction remove event
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "reaction_removed",
                            "reaction": reaction_data,
                        },
                    )
                    
        except Exception as e:
            logger.error(f"Error handling reaction: {str(e)}")

    def _add_reaction(self, user, message_id, emoji):
        """Add a reaction to a message."""
        try:
            bunch = Bunch.objects.get(id=self.bunch_id)
            message = Message.objects.get(
                id=message_id,
                channel__bunch=bunch
            )
            
            # Check if user is a member of the bunch
            if not bunch.members.filter(user=user).exists():
                logger.warning(f"User {user.username} not a member of bunch {bunch.name}")
                return None
            
            # Check if reaction already exists
            existing_reaction = Reaction.objects.filter(
                message=message,
                user=user,
                emoji=emoji
            ).first()
            
            if existing_reaction:
                logger.info(f"Reaction already exists: {emoji} by {user.username}")
                return None
            
            # Create the reaction
            reaction = Reaction.objects.create(
                message=message,
                user=user,
                emoji=emoji
            )
            
            logger.info(f"Reaction added: {emoji} by {user.username} to message {message_id}")
            
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
            
        except (Bunch.DoesNotExist, Message.DoesNotExist) as e:
            logger.error(f"Error adding reaction: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error adding reaction: {str(e)}")
            return None

    def _remove_reaction(self, user, message_id, emoji):
        """Remove a reaction from a message."""
        try:
            bunch = Bunch.objects.get(id=self.bunch_id)
            message = Message.objects.get(
                id=message_id,
                channel__bunch=bunch
            )
            
            # Find the reaction
            reaction = Reaction.objects.filter(
                message=message,
                user=user,
                emoji=emoji
            ).first()
            
            if not reaction:
                logger.warning(f"Reaction not found: {emoji} by {user.username}")
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
            
            # Delete the reaction
            reaction.delete()
            
            logger.info(f"Reaction removed: {emoji} by {user.username} from message {message_id}")
            
            return reaction_data
            
        except (Bunch.DoesNotExist, Message.DoesNotExist) as e:
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
                text_data=json.dumps({
                    "type": "reaction.new",
                    "reaction": reaction
                })
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
                text_data=json.dumps({
                    "type": "reaction.delete",
                    "reaction": reaction
                })
            )
        except Exception as e:
            logger.error(f"Error in reaction_removed: {str(e)}")

    async def chat_message(self, event):
        if not self._is_connected:
            logger.warning(
                "Received chat_message while not connected"
            )
            return

        try:
            message = event["message"]
            logger.info(
                f"Sending message to client: {message['id']}"
            )
            await self.send(
                text_data=json.dumps({"message": message})
            )
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}")
