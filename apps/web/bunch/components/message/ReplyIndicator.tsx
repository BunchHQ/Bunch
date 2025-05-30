"use client";

import { Message } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CornerDownRight, CornerLeftDown, CornerUpRight } from "lucide-react";

interface ReplyIndicatorProps {
  message: Message;
  onJumpToReply?: () => void;
  className?: string;
}

export function ReplyIndicator({
  message,
  onJumpToReply,
  className,
}: ReplyIndicatorProps) {
  if (!message.reply_to_preview) {
    return null;
  }

  const handleClick = () => {
    onJumpToReply?.();
  };

  return (
    <div className={cn("ml-10 pb-1", className)}>
      <button
        onClick={handleClick}
        className="flex items-center gap-1 w-full text-left truncate hover:underline focus:underline"
        style={{ padding: 0, margin: 0 }}
      >
        <span
          className="text-xs font-medium text-foreground truncate"
          style={{ maxWidth: 120 }}
        >
          {message.reply_to_preview.author.username}
        </span>
        <span
          className="text-xs text-muted-foreground truncate"
          style={{ maxWidth: 200 }}
        >
          {message.reply_to_preview.content}
        </span>
      </button>
    </div>
  );
}
