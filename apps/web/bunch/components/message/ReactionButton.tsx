"use client";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useWebSocket } from "@/lib/WebSocketProvider";
import { useWebSocketReactions } from "@/lib/hooks";
import { Reaction } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useAuth } from "@clerk/nextjs";
import { useState } from "react";

interface ReactionButtonProps {
  emoji: string;
  count: number;
  reactions: Reaction[];
  messageId: string;
  bunchId: string;
  hasUserReacted: boolean;
}

export function ReactionButton({
  emoji,
  count,
  reactions,
  messageId,
  bunchId,
  hasUserReacted,
}: ReactionButtonProps) {
  const { userId } = useAuth();
  const { sendReaction, isConnected } = useWebSocket();
  const { toggleReaction, loading } = useWebSocketReactions();
  const [isToggling, setIsToggling] = useState(false);

  const handleToggle = async () => {
    if (isToggling || loading || !isConnected) return;

    setIsToggling(true);
    try {
      await toggleReaction(messageId, emoji, sendReaction);
    } catch (error) {
      console.error("Failed to toggle reaction:", error);
    } finally {
      setIsToggling(false);
    }
  };

  // Get list of users who reacted with this emoji for tooltip
  const reactionUsers = reactions
    .filter((r) => r.emoji === emoji)
    .map((r) => r.user.username)
    .slice(0, 10); // Limit to first 10 users

  const tooltipText =
    reactionUsers.length > 0
      ? reactionUsers.join(", ") + (reactionUsers.length === 10 ? "..." : "")
      : "";

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-6 px-2 py-1 text-xs gap-1 transition-colors",
              hasUserReacted
                ? "bg-blue-100 border border-blue-300 text-blue-700 hover:bg-blue-200"
                : "hover:bg-accent"
            )}
            onClick={handleToggle}
            disabled={isToggling || loading || !isConnected}
          >
            <span className="text-sm">{emoji}</span>
            <span className="text-xs font-medium">{count}</span>
          </Button>
        </TooltipTrigger>
        {tooltipText && (
          <TooltipContent>
            <p>{tooltipText}</p>
          </TooltipContent>
        )}
      </Tooltip>
    </TooltipProvider>
  );
}
