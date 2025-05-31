"use client";

import { Button } from "@/components/ui/button";
import type { Message } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CornerDownRight, X } from "lucide-react";

interface ReplyComposerHeaderProps {
  replyingTo: Message;
  onCancel: () => void;
  className?: string;
  onJumpToReply?: () => void;
}

export function ReplyComposerHeader({
  replyingTo,
  onCancel,
  className,
  onJumpToReply,
}: ReplyComposerHeaderProps) {
  const handleClick = () => {
    onJumpToReply?.();
  };

  return (
    // biome-ignore lint/a11y/useKeyWithClickEvents: <explanation>
    <div
      onClick={handleClick}
      className={cn(
        "flex items-start gap-2 p-3 bg-accent/30 border-b border-border rounded-t-md",
        className,
      )}
    >
      <CornerDownRight className="h-4 w-4 text-muted-foreground mt-1 flex-shrink-0" />
      <div className="min-w-0 flex-1">
        <div className="text-sm font-medium text-foreground">
          Replying to {replyingTo.author.user.username}
        </div>
        <div className="text-sm text-muted-foreground mt-1 line-clamp-2">
          {replyingTo.content}
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={onCancel}
        className="h-6 w-6 p-0 hover:bg-background/50"
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}
