"use client";

import { useRef, useState } from "react";
import { useWebSocket } from "@/lib/WebSocketProvider";
import { Textarea } from "@/components/ui/textarea";
import { PaperclipIcon, SmileIcon, SendIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface MessageComposerProps {
  bunchId: string;
  channelId: string;
}

export function MessageComposer({ bunchId, channelId }: MessageComposerProps) {
  const [message, setMessage] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sendMessage, isConnected } = useWebSocket();

  const handleSendMessage = async () => {
    const trimmedMessage = message.trim();

    if (trimmedMessage && isConnected) {
      try {
        await sendMessage(trimmedMessage);
        setMessage("");

        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      } catch (error) {
        console.error("Error sending message:", error);
      }
    }
  };

  const handleKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      await handleSendMessage();
    }
  };

  return (
    <div
      className={cn(
        "border-t border-border p-4 transition-all",
        isFocused && "bg-accent/10"
      )}
    >
      <div className="flex items-end space-x-2">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="flex-shrink-0 rounded-full"
        >
          <PaperclipIcon className="h-5 w-5" />
        </Button>

        <div className="relative flex-1">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={`Message #${channelId}`}
            className="min-h-[40px] max-h-[200px] pr-10 resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-background"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-2 bottom-2 h-6 w-6 rounded-full"
          >
            <SmileIcon className="h-5 w-5" />
          </Button>
        </div>

        <Button
          type="button"
          size="icon"
          className={cn(
            "flex-shrink-0 rounded-full transition-opacity",
            (!message.trim() || !isConnected) && "opacity-50 cursor-not-allowed"
          )}
          onClick={handleSendMessage}
          disabled={!message.trim() || !isConnected}
        >
          <SendIcon className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
