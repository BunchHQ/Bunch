"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useWebSocket } from "@/lib/WebSocketProvider";
import { useMessages } from "@/lib/hooks";
import type { Message } from "@/lib/types";
import { Loader2 } from "lucide-react";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { MessageComposer } from "./MessageComposer";
import { MessageItem } from "./MessageItem";

export function MessageList() {
  const params = useParams();
  const bunchId = params?.bunchId as string;
  const channelId = params?.channelId as string;

  const {
    connectWebSocket,
    disconnectWebSocket,
    messages: wsMessages,
    isConnected,
  } = useWebSocket();

  const {
    messages,
    loading: isLoading,
    fetchMessages,
    setMessages,
  } = useMessages(bunchId, channelId);
  const scrollRef = useRef<HTMLDivElement>(null);
  const processedMessageIds = useRef<Set<string>>(new Set());
  const processedReactionIds = useRef<Set<string>>(new Set());
  const prevChannelRef = useRef<{ bunchId: string; channelId: string } | null>(
    null
  );

  // Reply state
  const [replyingTo, setReplyingTo] = useState<Message | undefined>(undefined);
  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, []);

  // Reply handlers
  const handleReply = useCallback((message: Message) => {
    setReplyingTo(message);
    // Focus the composer textarea when starting a reply
    setTimeout(() => {
      const textarea = document.querySelector(
        'textarea[placeholder*="Message"]'
      );
      if (textarea) {
        (textarea as HTMLTextAreaElement).focus();
      }
    }, 100);
  }, []);

  const handleCancelReply = useCallback(() => {
    setReplyingTo(undefined);
  }, []);

  const handleJumpToMessage = useCallback((messageId: string) => {
    // Find the message element and scroll to it
    const messageElement = document.querySelector(
      `[data-message-id="${messageId}"]`
    );
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: "smooth", block: "center" });
      // Add a brief highlight effect
      messageElement.classList.add("bg-accent/50");
      setTimeout(() => {
        messageElement.classList.remove("bg-accent/50");
      }, 2000);
    }
  }, []);

  // Initial fetch of messages and WebSocket connection
  useEffect(() => {
    const fetchInitialMessages = async () => {
      if (bunchId && channelId) {
        console.log("Fetching initial messages...");
        processedMessageIds.current = new Set();
        processedReactionIds.current = new Set();

        await fetchMessages();
        console.log("Fetched messages:", messages);

        if (messages && Array.isArray(messages)) {
          messages.forEach((msg) => {
            processedMessageIds.current.add(msg.id);
          });
        }

        setTimeout(scrollToBottom, 100);
      }
    };

    if (bunchId && channelId) {
      const currentChannel = { bunchId, channelId };

      // only connect if channel changed or not connected
      if (
        !prevChannelRef.current ||
        prevChannelRef.current.bunchId !== bunchId ||
        prevChannelRef.current.channelId !== channelId
      ) {
        if (prevChannelRef.current) {
          disconnectWebSocket();
        }

        connectWebSocket(bunchId, channelId);
        prevChannelRef.current = currentChannel;
        console.log(`Connecting to channel: ${bunchId}/${channelId}`);

        fetchInitialMessages();
      }
    }
  }, [
    bunchId,
    channelId,
    connectWebSocket,
    disconnectWebSocket,
    fetchMessages,
    messages,
    scrollToBottom,
  ]);

  // Handle reconnection when connection is lost
  useEffect(() => {
    if (!isConnected && bunchId && channelId) {
      const currentChannel = { bunchId, channelId };
      if (
        !prevChannelRef.current ||
        (prevChannelRef.current.bunchId === bunchId &&
          prevChannelRef.current.channelId === channelId)
      ) {
        console.log("Connection lost, attempting to reconnect...");
        connectWebSocket(bunchId, channelId);
        prevChannelRef.current = currentChannel;
      }
    }
  }, [isConnected, bunchId, channelId, connectWebSocket]);
  // Process new WebSocket messages
  useEffect(() => {
    if (wsMessages.length > 0) {
      console.log("Received WebSocket messages:", wsMessages);
      for (const wsMessage of wsMessages) {
        // Handle new message events
        if (
          wsMessage.message?.id &&
          !processedMessageIds.current.has(wsMessage.message.id)
        ) {
          processedMessageIds.current.add(wsMessage.message.id);

          setMessages((prev: Message[]) => {
            const newMessages = [...prev, wsMessage.message] as Message[];
            console.log("Updated messages with new message:", newMessages);
            return newMessages;
          });
        }
        // Handle reaction events
        else if (
          wsMessage.type === "reaction.new" ||
          wsMessage.type === "reaction.delete"
        ) {
          console.log("Processing reaction event:", wsMessage);
          const { reaction } = wsMessage;

          // Add type guard
          if (!reaction) {
            console.warn("Reaction event received without reaction data");
            continue;
          }

          if (!reaction.message_id) {
            console.warn("Reaction event received without message_id");
            continue;
          }

          // unique identifier for this reaction event
          const reactionEventId = `${wsMessage.type}-${reaction.id}-${reaction.message_id}-${reaction.emoji}-${reaction.user?.id}`;
          if (processedReactionIds.current.has(reactionEventId)) {
            console.log(
              `Reaction event ${reactionEventId} already processed, skipping`
            );
            continue;
          }
          processedReactionIds.current.add(reactionEventId);

          console.log("Reaction data:", reaction);

          setMessages((prev: Message[]) => {
            console.log("Current messages before reaction update:", prev);
            const updatedMessages = prev.map((msg) => {
              if (msg.id === reaction.message_id) {
                console.log(
                  `Found matching message ${reaction.message_id}, updating reactions`
                );
                let updatedReactions = [...(msg.reactions || [])];
                const updatedCounts = { ...(msg.reaction_counts || {}) };

                if (wsMessage.type === "reaction.new") {
                  console.log("Adding reaction:", reaction);
                  // Add the new reaction
                  updatedReactions.push(reaction);
                  updatedCounts[reaction.emoji] =
                    (updatedCounts[reaction.emoji] || 0) + 1;
                } else if (wsMessage.type === "reaction.delete") {
                  console.log("Removing reaction:", reaction);
                  // Remove the reaction
                  updatedReactions = updatedReactions.filter(
                    (r) => r.id !== reaction.id
                  );
                  updatedCounts[reaction.emoji] = Math.max(
                    (updatedCounts[reaction.emoji] || 1) - 1,
                    0
                  );
                  // Remove emoji from counts if count reaches 0
                  if (updatedCounts[reaction.emoji] === 0) {
                    delete updatedCounts[reaction.emoji];
                  }
                }

                console.log(
                  `Updated message ${reaction.message_id} reactions:`,
                  {
                    reactions: updatedReactions,
                    counts: updatedCounts,
                  }
                );

                return {
                  ...msg,
                  reactions: updatedReactions,
                  reaction_counts: updatedCounts,
                };
              }
              return msg;
            });

            console.log("Messages after reaction update:", updatedMessages);
            return updatedMessages;
          });
        }
      }

      setTimeout(scrollToBottom, 100);
    }
  }, [wsMessages, setMessages, scrollToBottom]);

  // Group messages by author, time, and reply
  const groupedMessages =
    messages?.reduce((groups: Message[][], message) => {
      if (!message || !message.author || !message.author.user) {
        console.warn("Invalid message format:", message);
        return groups;
      }

      const lastGroup = groups[groups.length - 1];

      // new group if:
      // 1. first message
      // 2. from a different author than the last group
      // 3. more than 5 minutes apart from the last message in the last group
      // 4. message is a reply (reply_to_id is present)
      if (
        !lastGroup ||
        lastGroup[0].author.user.id !== message.author.user.id ||
        new Date(message.created_at).getTime() -
          new Date(lastGroup[lastGroup.length - 1].created_at).getTime() >
          5 * 60 * 1000 ||
        message.reply_to_id // <-- new group if this is a reply
      ) {
        groups.push([message]);
      } else {
        lastGroup.push(message);
      }

      return groups;
    }, []) || [];

  console.log("Grouped messages:", groupedMessages);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Connection status indicator
  const ConnectionStatus = () => {
    if (!isConnected) {
      return (
        <div className="p-2 bg-yellow-100 text-yellow-800 rounded-md text-sm text-center">
          Reconnecting to chat...
        </div>
      );
    }
    return null;
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <ConnectionStatus />
      <ScrollArea ref={scrollRef} className="flex-1 overflow-y-auto p-4">
        {messages?.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-20">
            <div className="rounded-full bg-muted p-4 mb-4">
              <Avatar className="h-16 w-16">
                <AvatarFallback>📝</AvatarFallback>
              </Avatar>
            </div>
            <h3 className="text-xl font-semibold mb-2">No messages yet</h3>
            <p className="text-muted-foreground text-center max-w-md">
              Be the first to start a conversation in this channel!
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {groupedMessages?.map((group, index) => (
              <div key={`${group[0].id}-${index}`} className="space-y-0">
                <div data-message-id={group[0].id}>
                  <MessageItem
                    message={group[0]}
                    showHeader={true}
                    bunchId={bunchId}
                    onReply={handleReply}
                    onJumpToMessage={handleJumpToMessage}
                  />
                </div>
                {group.slice(1).map((message) => (
                  <div key={message.id} data-message-id={message.id}>
                    <MessageItem
                      message={message}
                      showHeader={false}
                      bunchId={bunchId}
                      onReply={handleReply}
                      onJumpToMessage={handleJumpToMessage}
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </ScrollArea>{" "}
      <div>
        <MessageComposer
          bunchId={bunchId}
          channelId={channelId}
          replyingTo={replyingTo}
          onCancelReply={handleCancelReply}
        />
      </div>
    </div>
  );
}
