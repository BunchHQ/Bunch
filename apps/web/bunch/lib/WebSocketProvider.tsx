"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from "react";
import { useAuth } from "@clerk/nextjs";
import { WebSocketMessage } from "@/lib/types";

// WebSocket connection states
enum ConnectionState {
  DISCONNECTED = "disconnected",
  CONNECTING = "connecting",
  CONNECTED = "connected",
  RECONNECTING = "reconnecting",
}

interface WebSocketContextType {
  connectWebSocket: (bunchId: string, channelId: string) => void;
  disconnectWebSocket: () => void;
  sendMessage: (content: string) => void;
  messages: WebSocketMessage[];
  isConnected: boolean;
  connectionState: ConnectionState;
}

const WebSocketContext = createContext<WebSocketContextType>({
  connectWebSocket: () => {},
  disconnectWebSocket: () => {},
  sendMessage: () => {},
  messages: [],
  isConnected: false,
  connectionState: ConnectionState.DISCONNECTED,
});

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    ConnectionState.DISCONNECTED
  );
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastPingTime = useRef<number>(0);
  const lastPongTime = useRef<number>(0);
  const { getToken } = useAuth();
  const currentChannelRef = useRef<{
    bunchId: string;
    channelId: string;
  } | null>(null);
  const isConnectingRef = useRef(false);
  // Use a persistent connection ID that doesn't change between reconnects
  const connectionIdRef = useRef<string>(
    typeof window !== "undefined"
      ? localStorage.getItem("bunch_connection_id") || crypto.randomUUID()
      : crypto.randomUUID()
  );

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("bunch_connection_id", connectionIdRef.current);
    }
  }, []);

  const connectWebSocket = useCallback(
    async (bunchId: string, channelId: string) => {
      // Prevent multiple connection attempts
      if (
        isConnectingRef.current ||
        (socketRef.current?.readyState === WebSocket.OPEN &&
          currentChannelRef.current?.bunchId === bunchId &&
          currentChannelRef.current?.channelId === channelId)
      ) {
        console.log("Already connecting or connected to the requested channel");
        return;
      }

      setConnectionState(
        reconnectAttempts.current > 0
          ? ConnectionState.RECONNECTING
          : ConnectionState.CONNECTING
      );

      try {
        // If we're already connected to the requested channel, don't reconnect
        if (
          socketRef.current?.readyState === WebSocket.OPEN &&
          currentChannelRef.current?.bunchId === bunchId &&
          currentChannelRef.current?.channelId === channelId
        ) {
          console.log("Already connected to the requested channel");
          return;
        }

        isConnectingRef.current = true;

        if (socketRef.current) {
          console.log("Closing existing connection before creating a new one");
          socketRef.current.close(1000, "User disconnected");
          socketRef.current = null;
        }

        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }

        const token = await getToken({ template: "Django" });
        if (!token) {
          console.error("No authentication token available");
          return;
        }

        // Add a keepalive parameter to indicate this is a persistent connection
        const wsUrl = `${
          process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
        }/ws/bunch/${bunchId}/channel/${channelId}/?token=${encodeURIComponent(
          token
        )}&connection_id=${connectionIdRef.current}&keepalive=true`; // Use the persistent connection ID with keepalive flag

        console.log("Connecting to WebSocket:", wsUrl);
        const socket = new WebSocket(wsUrl);
        socketRef.current = socket;
        currentChannelRef.current = { bunchId, channelId };

        // Define the ping interval function with heartbeat monitoring
        const startPingInterval = () => {
          // Clear any existing ping interval
          if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
          }

          // Send a ping every 15 seconds to keep the connection alive
          pingIntervalRef.current = setInterval(() => {
            if (socketRef.current?.readyState === WebSocket.OPEN) {
              try {
                // Check if we've received a pong since our last ping
                const now = Date.now();
                if (
                  lastPingTime.current > 0 &&
                  lastPongTime.current < lastPingTime.current &&
                  now - lastPingTime.current > 20000
                ) {
                  // No pong received for over 20 seconds after our last ping
                  console.warn(
                    "No pong received after last ping, connection may be dead"
                  );
                  socket.close(4000, "Heartbeat timeout");
                  return;
                }

                lastPingTime.current = now;
                socketRef.current.send(
                  JSON.stringify({ type: "ping", timestamp: now })
                );
                console.log("Ping sent to keep connection alive");
              } catch (error) {
                console.error("Error sending ping:", error);
              }
            }
          }, 15000);
        };

        const connectionTimeout = setTimeout(() => {
          if (socket.readyState !== WebSocket.OPEN) {
            console.log("Connection timeout - closing socket");
            socket.close();
            setIsConnected(false);
            isConnectingRef.current = false;
          }
        }, 5000);

        socket.onopen = () => {
          clearTimeout(connectionTimeout);
          console.log("WebSocket connected");
          setIsConnected(true);
          setConnectionState(ConnectionState.CONNECTED);
          isConnectingRef.current = false;
          // Reset reconnect attempts on successful connection
          reconnectAttempts.current = 0;
          lastPingTime.current = 0;
          lastPongTime.current = 0;
          // Start the ping interval to keep the connection alive
          startPingInterval();
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === "pong") {
              lastPongTime.current = Date.now();
              return;
            }

            console.log("Received WebSocket message:", data);

            if (data.type === "connection_established") {
              console.log("Connection established:", data);
              setIsConnected(true);
              setConnectionState(ConnectionState.CONNECTED);
              return;
            }

            if (data.message) {
              console.log("Adding new message to state:", data.message);
              setMessages((prev) => {
                // Check if message already exists to prevent duplicates
                const messageExists = prev.some(
                  (msg) => msg.message && msg.message.id === data.message.id
                );
                if (messageExists) {
                  return prev;
                }
                return [...prev, data];
              });
            }
          } catch (error) {
            console.error("Error parsing message:", error);
          }
        };

        socket.onclose = (event) => {
          clearTimeout(connectionTimeout);
          console.log("WebSocket disconnected:", event.code, event.reason);

          // Clear ping interval on close
          if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = null;
          }

          if (socket === socketRef.current) {
            setIsConnected(false);
            setConnectionState(ConnectionState.DISCONNECTED);
            socketRef.current = null;
            isConnectingRef.current = false;

            //reconnect only if we have a current channel and user didn't cause the closing
            // don't reconnect on auth errors (4001-4005)
            const isAuthError = event.code >= 4001 && event.code <= 4005;
            const isUserDisconnect =
              event.code === 1000 && event.reason.includes("User disconnected");
            const shouldReconnect =
              currentChannelRef.current && !isAuthError && !isUserDisconnect;

            if (shouldReconnect) {
              setConnectionState(ConnectionState.RECONNECTING);
              // Calculate backoff time: start with 1s, max 30s
              const backoffTime = Math.min(
                1000 * Math.pow(1.5, Math.min(reconnectAttempts.current, 10)),
                30000
              );
              console.log(
                `Scheduling reconnect in ${backoffTime}ms (attempt ${
                  reconnectAttempts.current + 1
                })`
              );

              reconnectTimeoutRef.current = setTimeout(() => {
                reconnectAttempts.current += 1;
                console.log(
                  `Attempting to reconnect... (attempt ${reconnectAttempts.current})`
                );
                connectWebSocket(
                  currentChannelRef.current!.bunchId,
                  currentChannelRef.current!.channelId
                );
              }, backoffTime);
            } else {
              currentChannelRef.current = null;
            }
          }
        };

        socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          clearTimeout(connectionTimeout);
          if (socket === socketRef.current) {
            setIsConnected(false);
            isConnectingRef.current = false;
          }
        };
      } catch (error) {
        console.error("Error connecting to WebSocket:", error);
        setIsConnected(false);
        isConnectingRef.current = false;
      }
    },
    [getToken]
  );

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (socketRef.current) {
      socketRef.current.close(1000, "User disconnected");
      socketRef.current = null;
    }

    currentChannelRef.current = null;
    isConnectingRef.current = false;
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      try {
        const message = { type: "message.new", content: content.trim() };
        console.log("Sending message:", message);
        socketRef.current.send(JSON.stringify(message));
      } catch (error) {
        console.error("Error sending message:", error);
        // Attempt to reconnect if sending fails
        if (socketRef.current) {
          socketRef.current.close();
          socketRef.current = null;
          setIsConnected(false);
        }
      }
    } else {
      console.error("WebSocket not connected");
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  return (
    <WebSocketContext.Provider
      value={{
        connectWebSocket,
        disconnectWebSocket,
        sendMessage,
        messages,
        isConnected,
        connectionState,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
