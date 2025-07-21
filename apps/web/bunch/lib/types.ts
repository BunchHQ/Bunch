export interface User {
  id: string
  email: string
  username: string
  avatar?: string
  status?: string
  bio?: string
  theme_preference: "light" | "dark" | "system"
  color: string
  pronoun?: string
}

export interface Bunch {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  owner: User
  icon?: string
  is_private: boolean
  invite_code?: string
  members_count: number
  primary_color?: string
}

export interface Member {
  id: string
  bunch: string // Bunch ID
  user: User
  role: "owner" | "admin" | "member"
  joined_at: string
  nickname?: string
}

export interface Channel {
  id: string
  bunch: string // Bunch ID
  name: string
  type: "text" | "voice" | "announcement"
  description?: string
  created_at: string
  is_private: boolean
  position: number
}

export interface Reaction {
  id: string
  message_id: string // Message ID (from backend serializer)
  user: User
  emoji: string
  created_at: string
}

export interface Message {
  id: string
  channel: string // Channel ID
  author: Member // Actually returns expanded Member object
  content: string
  created_at: string
  updated_at: string
  edit_count: number
  deleted: boolean
  deleted_at?: string
  reactions?: Reaction[]
  reaction_counts?: { [emoji: string]: number }
  reply_to_id?: string
  reply_to_preview?: {
    id: string
    content: string
    author: {
      id: string
      username: string
    }
    created_at: string
  }
  reply_count?: number
}

// must be kept in sync with server/bunch/constants.py
export enum WSMessageTypeClient {
  PING = "ping",
  SUBSCRIBE = "subscribe",
  UNSUBSCRIBE = "unsubscribe",
  // messages
  MESSAGE_NEW = "message.new",
  MESSAGE_UPDATE = "message.update",
  MESSAGE_DELETE = "message.delete",
  // reactions
  REACTION = "reaction",
  REACTION_NEW = "reaction.new",
  REACTION_DELETE = "reaction.delete",
  REACTION_TOGGLE = "reaction.toggle",
}

export enum WSMessageTypeServer {
  PONG = "pong",
  ERROR = "error",
  SUBSCRIBED = "subscribed",
  UNSUBSCRIBED = "unsubscribed",
  CHAT_MESSAGE = "chat.message",
  REACTION_NEW = "reaction.new",
  REACTION_DELETE = "reaction.delete",
}

export interface WebSocketMessage {
  type: WSMessageTypeClient
  message?: Message
  reaction?: Reaction
}
