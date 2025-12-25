"use client"

import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Smile } from "lucide-react"
import { useState } from "react"

interface EmojiPickerProps {
  onEmojiSelect: (emoji: string) => void
  trigger?: React.ReactNode
}

const COMMON_EMOJIS = [
  "👍",
  "👎",
  "❤️",
  "😂",
  "😮",
  "😢",
  "😡",
  "🎉",
  "👏",
  "🔥",
  "💯",
  "😍",
  "🤔",
  "👀",
  "🙏",
  "💪",
  "✨",
  "⭐",
  "🚀",
  "🎯",
]

export function EmojiPicker({ onEmojiSelect, trigger }: EmojiPickerProps) {
  const [open, setOpen] = useState(false)

  const handleEmojiClick = (emoji: string) => {
    onEmojiSelect(emoji)
    setOpen(false)
  }
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        {trigger || (
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            data-testid="emoji-picker-trigger"
          >
            <Smile className="h-4 w-4" />
          </Button>
        )}
      </PopoverTrigger>
      <PopoverContent className="w-80 p-4" align="start" data-testid="emoji-picker-content">
        <div className="grid grid-cols-8 gap-2">
          {COMMON_EMOJIS.map(emoji => (
            <Button
              key={emoji}
              variant="ghost"
              size="sm"
              className="hover:bg-accent h-8 w-8 p-0 text-lg"
              onClick={() => handleEmojiClick(emoji)}
            >
              {emoji}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  )
}
