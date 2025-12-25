"use client"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useEffect, useRef, useState } from "react"

interface MessageEditorProps {
  initialContent: string
  onSave: (content: string) => void
  onCancel: () => void
}

export function MessageEditor({ initialContent, onSave, onCancel }: MessageEditorProps) {
  const [content, setContent] = useState(initialContent)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus()
      textareaRef.current.setSelectionRange(content.length, content.length)
    }
  }, [content.length])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      onCancel()
    } else if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSave()
    }
  }

  const handleSave = () => {
    const trimmedContent = content.trim()
    if (trimmedContent && trimmedContent !== initialContent) {
      onSave(trimmedContent)
    } else if (trimmedContent === initialContent) {
      onCancel()
    }
  }

  return (
    <div className="space-y-2">
      <Textarea
        ref={textareaRef}
        value={content}
        onChange={e => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        className="min-h-20 resize-none"
        placeholder="Edit your message..."
      />
      <div className="text-muted-foreground flex items-center justify-end space-x-2 text-xs">
        <span>Press Esc to cancel, Enter to save</span>
        <div className="flex space-x-2">
          <Button variant="ghost" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button size="sm" onClick={handleSave}>
            Save
          </Button>
        </div>
      </div>
    </div>
  )
}
