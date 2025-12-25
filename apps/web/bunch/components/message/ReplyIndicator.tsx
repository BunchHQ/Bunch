"use client"

import type { Message } from "@/lib/types"
import { cn } from "@/lib/utils"

interface ReplyIndicatorProps {
  message: Message
  onJumpToReply?: () => void
  className?: string
}

export function ReplyIndicator({ message, onJumpToReply, className }: ReplyIndicatorProps) {
  if (!message.reply_to_preview) {
    return null
  }

  const handleClick = () => {
    onJumpToReply?.()
  }

  return (
    <div className={cn("ml-13 pb-1", className)}>
      <button
        onClick={handleClick}
        className="flex w-full items-center gap-1 truncate text-left hover:underline focus:underline"
        style={{ padding: 0, margin: 0 }}
        type="button"
      >
        <span className="text-foreground truncate text-xs font-medium" style={{ maxWidth: 120 }}>
          {message.reply_to_preview.author.username}
        </span>
        <span className="text-muted-foreground truncate text-xs" style={{ maxWidth: 200 }}>
          {message.reply_to_preview.content}
        </span>
      </button>
    </div>
  )
}
