"use client";

import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { useWebSocket } from "@/lib/WebSocketProvider";
import { useMessages } from "@/lib/hooks";
import type { Message } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Apple,
  Hand,
  Heart,
  Leaf,
  PaperclipIcon,
  Plane,
  SendIcon,
  Smartphone,
  Smile,
  SmileIcon,
  Trophy,
} from "lucide-react";
import { useRef, useState } from "react";
import { ReplyComposerHeader } from "./ReplyComposerHeader";

interface MessageComposerProps {
  bunchId: string;
  channelId: string;
  replyingTo?: Message;
  onCancelReply?: () => void;
  onJumpToMessage?: (messageId: string) => void;
}

const EMOJI_CATEGORIES = {
  faces: {
    name: "Faces",
    icon: Smile,
    emojis: [
      "😀",
      "😃",
      "😄",
      "😁",
      "😆",
      "😅",
      "😂",
      "🤣",
      "😊",
      "😇",
      "🙂",
      "🙃",
      "😉",
      "😌",
      "😍",
      "🥰",
      "😘",
      "😗",
      "😙",
      "😚",
      "😋",
      "😛",
      "😝",
      "😜",
      "🤪",
      "🤨",
      "🧐",
      "🤓",
      "😎",
      "🤩",
      "🥳",
      "😏",
      "😒",
      "😞",
      "😔",
      "😟",
      "😕",
      "🙁",
      "☹️",
      "😣",
      "😖",
      "😫",
      "😩",
      "🥺",
      "😢",
      "😭",
      "😤",
      "😠",
      "😡",
      "🤬",
      "🤯",
      "😳",
      "🥵",
      "🥶",
      "😱",
      "😨",
      "😰",
      "😥",
      "😓",
      "🤗",
      "🤔",
      "🤭",
      "🤫",
      "🤥",
    ],
  },
  gestures: {
    name: "Gestures",
    icon: Hand,
    emojis: [
      "👋",
      "🤚",
      "🖐️",
      "✋",
      "🖖",
      "👌",
      "🤌",
      "🤏",
      "✌️",
      "🤞",
      "🤟",
      "🤘",
      "🤙",
      "👈",
      "👉",
      "👆",
      "🖕",
      "👇",
      "☝️",
      "👍",
      "👎",
      "✊",
      "👊",
      "🤛",
      "🤜",
      "👏",
      "🙌",
      "👐",
      "🤲",
      "🤝",
      "🙏",
      "✍️",
    ],
  },
  hearts: {
    name: "Hearts",
    icon: Heart,
    emojis: [
      "❤️",
      "🧡",
      "💛",
      "💚",
      "💙",
      "💜",
      "🖤",
      "🤍",
      "🤎",
      "💔",
      "❤️‍🔥",
      "❤️‍🩹",
      "💖",
      "💗",
      "💓",
      "💞",
      "💕",
      "💟",
      "❣️",
      "💝",
      "💘",
      "💌",
      "💋",
      "💯",
      "💢",
      "💥",
      "💫",
      "💦",
      "💨",
      "🕳️",
      "💣",
      "💬",
    ],
  },
  nature: {
    name: "Nature",
    icon: Leaf,
    emojis: [
      "🌱",
      "🌲",
      "🌳",
      "🌴",
      "🌵",
      "🌾",
      "🌿",
      "☘️",
      "🍀",
      "🍁",
      "🍂",
      "🍃",
      "🌺",
      "🌸",
      "🌼",
      "🌻",
      "🌞",
      "🌝",
      "🌛",
      "🌜",
      "🌚",
      "🌕",
      "🌖",
      "🌗",
      "🌘",
      "🌑",
      "🌒",
      "🌓",
      "🌔",
      "🌙",
      "🌎",
      "🌍",
    ],
  },
  food: {
    name: "Food",
    icon: Apple,
    emojis: [
      "🍎",
      "🍐",
      "🍊",
      "🍋",
      "🍌",
      "🍉",
      "🍇",
      "🍓",
      "🫐",
      "🍈",
      "🍒",
      "🍑",
      "🥭",
      "🍍",
      "🥥",
      "🥝",
      "🍅",
      "🍆",
      "🥑",
      "🥦",
      "🥬",
      "🥒",
      "🌶️",
      "🫑",
      "🌽",
      "🥕",
      "🫒",
      "🧄",
      "🧅",
      "🥔",
      "🍠",
      "🥐",
    ],
  },
  activities: {
    name: "Activities",
    icon: Trophy,
    emojis: [
      "⚽",
      "🏀",
      "🏈",
      "⚾",
      "🥎",
      "🎾",
      "🏐",
      "🏉",
      "🎱",
      "🏓",
      "🏸",
      "🏒",
      "🏑",
      "🥍",
      "🏏",
      "🥊",
      "🥋",
      "🥅",
      "⛳",
      "⛸️",
      "🎣",
      "🤿",
      "🎽",
      "🛹",
      "🛷",
      "⛷️",
      "🏂",
      "🏋️",
      "🤼",
      "🤸",
      "⛹️",
      "🤾",
    ],
  },
  travel: {
    name: "Travel",
    icon: Plane,
    emojis: [
      "✈️",
      "🛫",
      "🛬",
      "🛩️",
      "💺",
      "🛰️",
      "🚀",
      "🛸",
      "🚁",
      "🛶",
      "⛵",
      "🚤",
      "🛥️",
      "🛳️",
      "⛴️",
      "🚢",
      "🚗",
      "🚕",
      "🚙",
      "🚌",
      "🚎",
      "🏎️",
      "🚓",
      "🚑",
      "🚒",
      "🚐",
      "🚚",
      "🚛",
      "🚜",
      "🛴",
      "🚲",
      "🛵",
    ],
  },
  objects: {
    name: "Objects",
    icon: Smartphone,
    emojis: [
      "⌚",
      "📱",
      "📲",
      "💻",
      "⌨️",
      "🖥️",
      "🖨️",
      "🖱️",
      "🖲️",
      "🕹️",
      "🗜️",
      "💽",
      "💾",
      "💿",
      "📀",
      "📼",
      "📷",
      "📸",
      "📹",
      "🎥",
      "📽️",
      "🎞️",
      "📞",
      "☎️",
      "📟",
      "📠",
      "📺",
      "📻",
      "🎙️",
      "🎚️",
      "🎛️",
      "🧭",
    ],
  },
};

export function MessageComposer({
  bunchId,
  channelId,
  replyingTo,
  onCancelReply,
  onJumpToMessage,
}: MessageComposerProps) {
  const [message, setMessage] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [hoverEmoji, setHoverEmoji] = useState("😊");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sendMessage: sendWebSocketMessage, isConnected } = useWebSocket();
  const { sendMessage: sendAPIMessage } = useMessages(bunchId, channelId);

  const hoverEmojis = ["😊", "😄", "😉", "😎", "🥰", "🤩", "😋", "🤗"];

  const handleEmojiHover = () => {
    const randomIndex = Math.floor(Math.random() * hoverEmojis.length);
    setHoverEmoji(hoverEmojis[randomIndex]);
  };

  const handleEmojiLeave = () => {
    setHoverEmoji("😊");
  };

  const handleSendMessage = async () => {
    const trimmedMessage = message.trim();

    if (trimmedMessage && isConnected) {
      try {
        if (replyingTo) {
          // For replies, use the API directly to include reply_to_id
          await sendAPIMessage(trimmedMessage, replyingTo.id);
          onCancelReply?.(); // Clear the reply state after sending
        } else {
          // For regular messages, use WebSocket as before
          await sendWebSocketMessage(trimmedMessage);
        }

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

  const handleOnJumpToReply = () => {
    if (replyingTo) {
      onJumpToMessage?.(replyingTo.id);
    }
  };

  const insertEmoji = (emoji: string) => {
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    const textBeforeCursor = message.substring(0, cursorPosition);
    const textAfterCursor = message.substring(cursorPosition);

    setMessage(textBeforeCursor + emoji + textAfterCursor);

    // Set cursor position after the inserted emoji
    setTimeout(() => {
      if (textareaRef.current) {
        const newPosition = cursorPosition + emoji.length;
        textareaRef.current.setSelectionRange(newPosition, newPosition);
        textareaRef.current.focus();
      }
    }, 0);
  };

  return (
    <div>
      {/* Reply header if replying to a message */}
      {replyingTo && (
        <ReplyComposerHeader
          replyingTo={replyingTo}
          onCancel={onCancelReply!}
          onJumpToReply={handleOnJumpToReply}
        />
      )}

      <div
        className={cn(
          "border-t border-border p-4 transition-all",
          isFocused && "bg-accent/10",
          replyingTo && "border-t-0 rounded-b-md",
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
            <div className="absolute right-2 bottom-1">
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 rounded-full relative group flex items-center justify-center"
                    onMouseEnter={handleEmojiHover}
                    onMouseLeave={handleEmojiLeave}
                  >
                    <span className="absolute inset-0 flex items-center justify-center text-2xl transition-opacity duration-200 group-hover:opacity-0">
                      <SmileIcon className="h-8 w-8 " />
                    </span>
                    <span className="absolute inset-0 flex items-center justify-center text-2xl opacity-0 transition-opacity duration-200 group-hover:opacity-100">
                      {hoverEmoji}
                    </span>
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-[400px] p-0" align="end">
                  <Tabs defaultValue="faces" className="w-full">
                    <TabsList className="w-full justify-start h-9 px-2 overflow-x-auto [&::-webkit-scrollbar]:h-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-muted-foreground/20 hover:[&::-webkit-scrollbar-thumb]:bg-muted-foreground/30">
                      {Object.entries(EMOJI_CATEGORIES).map(
                        ([key, { icon: Icon }]) => (
                          <TabsTrigger
                            key={key}
                            value={key}
                            className="h-7 w-7 p-0"
                          >
                            <Icon className="h-4 w-4" />
                          </TabsTrigger>
                        ),
                      )}
                    </TabsList>
                    <div className="h-[300px]">
                      {Object.entries(EMOJI_CATEGORIES).map(
                        ([key, { emojis }]) => (
                          <TabsContent
                            key={key}
                            value={key}
                            className="mt-0 h-full"
                          >
                            <div className="grid grid-cols-8 gap-1 p-2 h-full overflow-y-auto [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-muted-foreground/20 hover:[&::-webkit-scrollbar-thumb]:bg-muted-foreground/30">
                              {emojis.map((emoji, index) => (
                                <button
                                  key={index}
                                  onClick={() => insertEmoji(emoji)}
                                  className="hover:bg-accent p-2 rounded-md transition-colors text-lg"
                                >
                                  {emoji}
                                </button>
                              ))}
                            </div>
                          </TabsContent>
                        ),
                      )}
                    </div>
                  </Tabs>
                </PopoverContent>
              </Popover>
            </div>
          </div>{" "}
          <Button
            type="button"
            size="icon"
            className={cn(
              "flex-shrink-0 rounded-full transition-opacity",
              (!message.trim() || !isConnected) &&
                "opacity-50 cursor-not-allowed",
            )}
            onClick={handleSendMessage}
            disabled={!message.trim() || !isConnected}
          >
            <SendIcon className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
