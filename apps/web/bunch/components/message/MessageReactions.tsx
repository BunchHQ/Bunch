"use client";

import { Button } from "@/components/ui/button";
import { useWebSocket } from "@/lib/WebSocketProvider";
import { useWebSocketReactions } from "@/lib/hooks";
import type { Reaction } from "@/lib/types";
import { useAuth } from "@clerk/nextjs";
import { Plus } from "lucide-react";
import { EmojiPicker } from "./EmojiPicker";
import { ReactionButton } from "./ReactionButton";

interface MessageReactionsProps {
  messageId: string;
  reactions: Reaction[];
  reactionCounts: { [emoji: string]: number };
}

export function MessageReactions({
  messageId,
  reactions,
  reactionCounts,
}: MessageReactionsProps) {
  const { userId } = useAuth();
  const { sendReaction, isConnected } = useWebSocket();
  const { toggleReaction } = useWebSocketReactions();

  // Get unique emojis that have reactions
  const emojiList = Object.keys(reactionCounts).filter(
    (emoji) => reactionCounts[emoji] > 0,
  );

  const handleEmojiSelect = async (emoji: string) => {
    if (!isConnected) {
      console.error("WebSocket not connected");
      return;
    }

    try {
      await toggleReaction(messageId, emoji, sendReaction);
    } catch (error) {
      console.error("Failed to add reaction:", error);
    }
  };

  // Check if current user has reacted with specific emoji
  const hasUserReacted = (emoji: string) => {
    return reactions.some(
      (r) => r.emoji === emoji && r.user.username === userId,
    );
  };

  if (emojiList.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center gap-1 mt-1">
      {emojiList.map((emoji) => (
        <ReactionButton
          key={emoji}
          emoji={emoji}
          count={reactionCounts[emoji]}
          reactions={reactions}
          messageId={messageId}
          hasUserReacted={hasUserReacted(emoji)}
        />
      ))}{" "}
      <EmojiPicker
        onEmojiSelect={handleEmojiSelect}
        trigger={
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
            data-testid="reactions-emoji-picker-trigger"
          >
            <Plus className="h-3 w-3" />
          </Button>
        }
      />
    </div>
  );
}
