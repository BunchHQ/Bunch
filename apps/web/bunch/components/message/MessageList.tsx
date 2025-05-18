"use client";

import { useEffect, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import { useWebSocket } from "@/lib/WebSocketProvider";
import { Message } from "@/lib/types";
import { Loader2 } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageItem } from "./MessageItem";
import { MessageComposer } from "./MessageComposer";
import { useMessages } from "@/lib/hooks";

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
  const prevChannelRef = useRef<{ bunchId: string; channelId: string } | null>(
    null
  );

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, []);

  // Initial fetch of messages and WebSocket connection
  useEffect(() => {
    const fetchInitialMessages = async () => {
      if (bunchId && channelId) {
        console.log("Fetching initial messages...");
        processedMessageIds.current = new Set();

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
        if (
          wsMessage.message &&
          wsMessage.message.id &&
          !processedMessageIds.current.has(wsMessage.message.id)
        ) {
          processedMessageIds.current.add(wsMessage.message.id);

          setMessages((prev: Message[]) => {
            const newMessages = [...prev, wsMessage.message];
            console.log("Updated messages:", newMessages);
            return newMessages;
          });
        }
      }

      setTimeout(scrollToBottom, 100);
    }
  }, [wsMessages, setMessages, scrollToBottom]);

  // Group messages by author and time
  const groupedMessages =
    messages?.reduce((groups: Message[][], message) => {
      if (!message || !message.author || !message.author.user) {
        console.warn("Invalid message format:", message);
        return groups;
      }

      const lastGroup = groups[groups.length - 1];

      // Start new group if:
      // 1. first message
      //  2. from a different author than the last group
      // 3. more than 5 minutes apart from the last message in the last group
      if (
        !lastGroup ||
        lastGroup[0].author.user.id !== message.author.user.id ||
        new Date(message.created_at).getTime() -
          new Date(lastGroup[lastGroup.length - 1].created_at).getTime() >
          5 * 60 * 1000
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
          <div className="space-y-6">
            {groupedMessages?.map((group, index) => (
              <div key={`${group[0].id}-${index}`} className="space-y-1">
                <MessageItem
                  message={group[0]}
                  showHeader={true}
                  bunchId={bunchId}
                />
                {group.slice(1).map((message) => (
                  <MessageItem
                    key={message.id}
                    message={message}
                    showHeader={false}
                    bunchId={bunchId}
                  />
                ))}
              </div>
            ))}
          </div>
        )}
      </ScrollArea>

      <div>
        <MessageComposer bunchId={bunchId} channelId={channelId} />
      </div>
    </div>
  );
}
