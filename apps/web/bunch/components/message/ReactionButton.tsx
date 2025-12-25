"use client"

import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useWebSocketReactions } from "@/lib/hooks"
import type { Reaction } from "@/lib/types"
import { cn } from "@/lib/utils"
import { useWebSocket } from "@/lib/WebSocketProvider"
import { useState } from "react"

interface ReactionButtonProps {
  emoji: string
  count: number
  reactions: Reaction[]
  bunchId: string
  channelId: string
  messageId: string
  hasUserReacted: boolean
}

export function ReactionButton({
  emoji,
  count,
  reactions,
  bunchId,
  channelId,
  messageId,
  hasUserReacted,
}: ReactionButtonProps) {
  const { sendReaction, isConnected } = useWebSocket()
  const { toggleReaction, loading } = useWebSocketReactions()
  const [isToggling, setIsToggling] = useState(false)

  const handleToggle = async () => {
    if (isToggling || loading || !isConnected) return

    setIsToggling(true)
    try {
      await toggleReaction(bunchId, channelId, messageId, emoji, sendReaction)
    } catch (error) {
      console.error("Failed to toggle reaction:", error)
    } finally {
      setIsToggling(false)
    }
  }

  // Get list of users who reacted with this emoji for tooltip
  const reactionUsers = reactions
    .filter(r => r.emoji === emoji)
    .map(r => r.user.username)
    .slice(0, 10) // Limit to first 10 users

  const tooltipText =
    reactionUsers.length > 0
      ? reactionUsers.join(", ") + (reactionUsers.length === 10 ? "..." : "")
      : ""

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-6 gap-1 px-2 py-1 text-xs transition-colors",
              hasUserReacted
                ? "border border-blue-300 bg-blue-100 text-blue-700 hover:bg-blue-200 dark:border-blue-700 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800"
                : "hover:bg-accent border border-gray-200 dark:border-gray-700",
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
  )
}
