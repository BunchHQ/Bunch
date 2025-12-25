"use client"

import { Button } from "@/components/ui/button"
import type { Message } from "@/lib/types"
import { cn } from "@/lib/utils"
import { CornerDownRight, X } from "lucide-react"

interface ReplyComposerHeaderProps {
  replyingTo: Message
  onCancel: () => void
  className?: string
  onJumpToReply?: () => void
}

export function ReplyComposerHeader({
  replyingTo,
  onCancel,
  className,
  onJumpToReply,
}: ReplyComposerHeaderProps) {
  const handleClick = () => {
    onJumpToReply?.()
  }

  return (
    // biome-ignore lint/a11y/useKeyWithClickEvents: <explanation>
    <div
      onClick={handleClick}
      className={cn(
        "bg-accent/30 border-border flex items-start gap-2 rounded-t-md border-b p-3",
        className,
      )}
      data-testid="message-compose-reply-header"
    >
      <CornerDownRight className="text-muted-foreground mt-1 h-4 w-4 shrink-0" />
      <div className="min-w-0 flex-1">
        <div className="text-foreground text-sm font-medium">
          Replying to {replyingTo.author.user.username}
        </div>
        <div className="text-muted-foreground mt-1 line-clamp-2 text-sm">{replyingTo.content}</div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={onCancel}
        className="hover:bg-background/50 h-6 w-6 p-0"
      >
        <X className="h-4 w-4" />
        <span className="sr-only">Cancel</span>
      </Button>
    </div>
  )
}
