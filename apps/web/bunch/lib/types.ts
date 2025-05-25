export interface User {
  id: string;
  email: string;
  username: string;
  avatar?: string;
  status?: string;
  bio?: string;
  theme_preference: "light" | "dark" | "system";
  color: string;
  pronoun?: string;
}

export interface Bunch {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  owner: User;
  icon?: string;
  is_private: boolean;
  invite_code?: string;
  members_count: number;
  primary_color?: string;
}

export interface Member {
  id: string;
  bunch: string; // Bunch ID
  user: User;
  role: "owner" | "admin" | "member";
  joined_at: string;
  nickname?: string;
}

export interface Channel {
  id: string;
  bunch: string; // Bunch ID
  name: string;
  type: "text" | "voice" | "announcement";
  description?: string;
  created_at: string;
  is_private: boolean;
  position: number;
}

export interface Message {
  id: string;
  channel: string; // Channel ID
  author: Member;  // Actually returns expanded Member object
  content: string;
  created_at: string;
  updated_at: string;
  edit_count: number;
  deleted: boolean;
  deleted_at?: string;
}

export interface WebSocketMessage {
  type: "message.new" | "message.update" | "message.delete" | "ping";
  message: Message;
}
