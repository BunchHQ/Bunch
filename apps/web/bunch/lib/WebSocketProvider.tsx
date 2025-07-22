"use client"

import { useAuth } from "@clerk/nextjs"
import type React from "react"
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react"
import { type WebSocketMessage, WSMessageTypeClient, WSMessageTypeServer } from "@/lib/types"

// WebSocket connection states
enum ConnectionState {
  DISCONNECTED = "disconnected",
  CONNECTING = "connecting",
  CONNECTED = "connected",
  RECONNECTING = "reconnecting",
}

interface WebSocketContextType {
  connectWebSocket: () => void
  disconnectWebSocket: () => void
  subscribe: (bunchId: string, channelId: string) => void
  unsubscribe: (bunchId: string, channelId: string) => void
  sendMessage: (bunchId: string, channelId: string, content: string) => Promise<void>
  sendReaction: (bunchId: string, channelId: string, messageId: string, emoji: string) => void
  messages: WebSocketMessage[]
  isConnected: boolean
  connectionState: ConnectionState
}

const WebSocketContext = createContext<WebSocketContextType>({
  connectWebSocket: () => {},
  disconnectWebSocket: () => {},
  subscribe: () => {},
  unsubscribe: () => {},
  sendMessage: async () => {},
  sendReaction: () => {},
  messages: [],
  isConnected: false,
  connectionState: ConnectionState.DISCONNECTED,
})

export const useWebSocket = () => useContext(WebSocketContext)

const getSubscriptionKey = (bunchId: string, channelId: string) => {
  return JSON.stringify({ bunchId, channelId })
}

const getSubscriptionFromKey = (sKey: string) => {
  const sub: { bunchId: string; channelId: string } = JSON.parse(sKey)
  return sub
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    ConnectionState.DISCONNECTED,
  )
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const lastPingTime = useRef<number>(0)
  const lastPongTime = useRef<number>(0)

  const { getToken } = useAuth()

  const isConnectingRef = useRef(false)
  // Use a persistent connection ID that doesn't change between reconnects
  const connectionIdRef = useRef<string>(
    typeof window !== "undefined"
      ? localStorage.getItem("bunch_connection_id") || crypto.randomUUID()
      : crypto.randomUUID(),
  )

  const subscriptionsRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("bunch_connection_id", connectionIdRef.current)
    }
  }, [])

  const connectWebSocket = useCallback(async () => {
    // Prevent multiple connection attempts
    if (isConnectingRef.current || socketRef.current?.readyState === WebSocket.OPEN) {
      console.log("Already connecting or connected")
      return
    }

    setConnectionState(
      reconnectAttempts.current > 0 ? ConnectionState.RECONNECTING : ConnectionState.CONNECTING,
    )
    try {
      isConnectingRef.current = true

      if (socketRef.current) {
        console.log("Closing existing connection before creating a new one")
        socketRef.current.close(1000, "User disconnected")
        socketRef.current = null
      }

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }

      const token = await getToken({ template: "Django" })
      if (!token) {
        console.error("No authentication token available")
        return
      }

      // Add a keepalive parameter to indicate this is a persistent connection
      const wsUrl = `${
        process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
      }/ws/bunch/?token=${encodeURIComponent(
        token,
      )}&connection_id=${connectionIdRef.current}&keepalive=true` // Use the persistent connection ID with keepalive flag

      console.log("Connecting to WebSocket:", wsUrl)
      const socket = new WebSocket(wsUrl)
      socketRef.current = socket

      // Define the ping interval function with heartbeat monitoring
      const startPingInterval = () => {
        // Clear any existing ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current)
        }

        // Send a ping every 15 seconds to keep the connection alive
        pingIntervalRef.current = setInterval(() => {
          if (socketRef.current?.readyState === WebSocket.OPEN) {
            try {
              // Check if we've received a pong since our last ping
              const now = Date.now()
              if (
                lastPingTime.current > 0 &&
                lastPongTime.current < lastPingTime.current &&
                now - lastPingTime.current > 20000
              ) {
                // No pong received for over 20 seconds after our last ping
                console.warn("No pong received after last ping, connection may be dead")
                socket.close(4000, "Heartbeat timeout")
                return
              }

              lastPingTime.current = now
              socketRef.current.send(
                JSON.stringify({
                  type: WSMessageTypeClient.PING,
                  timestamp: now,
                }),
              )
              console.log("Ping sent to keep connection alive")
            } catch (error) {
              console.error("Error sending ping:", error)
            }
          }
        }, 15000)
      }

      const connectionTimeout = setTimeout(() => {
        if (socket.readyState !== WebSocket.OPEN) {
          console.log("Connection timeout - closing socket")
          socket.close()
          setIsConnected(false)
          isConnectingRef.current = false
        }
      }, 5000)

      socket.onopen = () => {
        clearTimeout(connectionTimeout)
        console.log("WebSocket connected")
        setIsConnected(true)
        setConnectionState(ConnectionState.CONNECTED)
        isConnectingRef.current = false
        // Reset reconnect attempts on successful connection
        reconnectAttempts.current = 0
        lastPingTime.current = 0
        lastPongTime.current = 0
        // Start the ping interval to keep the connection alive
        startPingInterval()

        if (subscriptionsRef.current.size > 0) {
          // subscribe to all subscriptions
          console.log("Subscribing to all subscriptions")
          for (const sub of subscriptionsRef.current) {
            const { bunchId, channelId } = getSubscriptionFromKey(sub)
            const payload = {
              type: WSMessageTypeClient.SUBSCRIBE,
              bunch_id: bunchId,
              channel_id: channelId,
            }
            console.log("Sending subscribe:", payload)
            socket.send(JSON.stringify(payload))
          }
        }
      }

      socket.onmessage = event => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === WSMessageTypeServer.PONG) {
            lastPongTime.current = Date.now()
            return
          }

          console.log("Received WebSocket message:", data)

          // handle message types
          if (data.type === "connection_established") {
            console.log("Connection established:", data)
            setIsConnected(true)
            setConnectionState(ConnectionState.CONNECTED)

            // Handle message events
          } else if (data.type === WSMessageTypeServer.CHAT_MESSAGE) {
            console.log("Adding new message to state:", data.message)
            setMessages(prev => {
              // Check if message already exists to prevent duplicates
              const messageExists = prev.some(
                msg => msg.message && msg.message.id === data.message.id,
              )
              if (messageExists) {
                return prev
              }
              return [...prev, data]
            })

            // Handle reaction events
          } else if (
            data.type === WSMessageTypeServer.REACTION_NEW ||
            data.type === WSMessageTypeServer.REACTION_DELETE
          ) {
            console.log("Received reaction event:", data)
            // they will go in messages too, bc components depend on messages
            // no need to update state separately
            setMessages(prev => [...prev, data])

            // Handle subscription event
          } else if (data.type === WSMessageTypeServer.SUBSCRIBED) {
            console.log("Subscribed to:", data.message)
            subscriptionsRef.current.add(getSubscriptionKey(data.bunch_id, data.channel_id))

            // Handle unsubscription event
          } else if (data.type === WSMessageTypeServer.UNSUBSCRIBED) {
            console.log("Unsubscribed from:", data.message)
            subscriptionsRef.current.delete(getSubscriptionKey(data.bunch_id, data.channel_id))

            // Handle error event
          } else if (data.type === WSMessageTypeServer.ERROR) {
            console.error("Error:", data.message)
          } else {
            console.warn("Unknown message type:", data.type, data)
          }
        } catch (error) {
          console.error("Error parsing message:", error)
        }
      }

      socket.onclose = event => {
        clearTimeout(connectionTimeout)
        console.log("WebSocket disconnected:", event.code, event.reason)

        // Clear ping interval on close
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current)
          pingIntervalRef.current = null
        }

        if (socket === socketRef.current) {
          setIsConnected(false)
          setConnectionState(ConnectionState.DISCONNECTED)
          socketRef.current = null
          isConnectingRef.current = false

          //reconnect only if we have a current channel and user didn't cause the closing
          // don't reconnect on auth errors (4001-4005)
          const isAuthError = event.code >= 4001 && event.code <= 4005
          const isUserDisconnect = event.code === 1000 && event.reason.includes("User disconnected")
          const shouldReconnect =
            subscriptionsRef.current.size > 0 && !isAuthError && !isUserDisconnect

          if (shouldReconnect) {
            setConnectionState(ConnectionState.RECONNECTING)
            // Calculate backoff time: start with 1s, max 30s
            const backoffTime = Math.min(
              1000 * 1.5 ** Math.min(reconnectAttempts.current, 10),
              30000,
            )
            console.log(
              `Scheduling reconnect in ${backoffTime}ms (attempt ${reconnectAttempts.current + 1})`,
            )

            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttempts.current += 1
              console.log(`Attempting to reconnect... (attempt ${reconnectAttempts.current})`)
              connectWebSocket()
            }, backoffTime)
          } else {
            subscriptionsRef.current.clear()
          }
        }
      }

      socket.onerror = error => {
        console.error("WebSocket error:", error)
        clearTimeout(connectionTimeout)
        if (socket === socketRef.current) {
          setIsConnected(false)
          isConnectingRef.current = false
        }
      }
    } catch (error) {
      console.error("Error connecting to WebSocket:", error)
      setIsConnected(false)
      isConnectingRef.current = false
    }
  }, [getToken])

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (socketRef.current) {
      // unsubscribe from all subscriptions
      if (subscriptionsRef.current.size > 0) {
        console.log("Unsubscribing from all subscriptions")
        for (const sub of subscriptionsRef.current) {
          const { bunchId, channelId } = getSubscriptionFromKey(sub)
          const payload = {
            type: WSMessageTypeClient.UNSUBSCRIBE,
            bunch_id: bunchId,
            channel_id: channelId,
          }
          console.log("Sending unsubscribe:", payload)
          socketRef.current.send(JSON.stringify(payload))
        }
      }

      socketRef.current.close(1000, "User disconnected")
      socketRef.current = null
    }

    isConnectingRef.current = false
    setIsConnected(false)
  }, [])

  // make ws connection on load
  useEffect(() => {
    connectWebSocket()

    return () => {
      disconnectWebSocket()
    }
  }, [connectWebSocket, disconnectWebSocket])

  const subscribe = useCallback((bunchId: string, channelId: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      if (subscriptionsRef.current.has(getSubscriptionKey(bunchId, channelId))) {
        console.log("Already subscribed to:", bunchId, channelId)
        return
      }

      try {
        const payload = {
          type: WSMessageTypeClient.SUBSCRIBE,
          bunch_id: bunchId,
          channel_id: channelId,
        }
        console.log("Sending subscribe:", payload)
        socketRef.current.send(JSON.stringify(payload))
      } catch (error) {
        console.error("Error subscribing:", error)
        // Attempt to reconnect if sending fails
        if (socketRef.current) {
          socketRef.current.close()
          socketRef.current = null
          setIsConnected(false)
        }
      }
    } else {
      console.error("WebSocket not connected")
    }
  }, [])

  const unsubscribe = useCallback((bunchId: string, channelId: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      if (!subscriptionsRef.current.has(getSubscriptionKey(bunchId, channelId))) {
        console.error("Not subscribed to", bunchId, channelId)
        return
      }

      try {
        const payload = {
          type: WSMessageTypeClient.UNSUBSCRIBE,
          bunch_id: bunchId,
          channel_id: channelId,
        }
        console.log("Sending unsubscribe:", payload)
        socketRef.current.send(JSON.stringify(payload))
      } catch (error) {
        console.error("Error unsubscribing:", error)
        // Attempt to reconnect if sending fails
        if (socketRef.current) {
          socketRef.current.close()
          socketRef.current = null
          setIsConnected(false)
        }
      }
    } else {
      console.error("WebSocket not connected")
    }
  }, [])

  const sendMessage = useCallback(async (bunchId: string, channelId: string, content: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      try {
        const message = {
          type: WSMessageTypeClient.MESSAGE_NEW,
          bunch_id: bunchId,
          channel_id: channelId,
          content: content.trim(),
        }
        console.log("Sending message:", message)
        socketRef.current.send(JSON.stringify(message))
      } catch (error) {
        console.error("Error sending message:", error)
        // Attempt to reconnect if sending fails
        if (socketRef.current) {
          socketRef.current.close()
          socketRef.current = null
          setIsConnected(false)
        }
      }
    } else {
      console.error("WebSocket not connected")
    }
  }, [])

  const sendReaction = useCallback(
    (bunchId: string, channelId: string, messageId: string, emoji: string) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        try {
          const reactionMessage = {
            type: WSMessageTypeClient.REACTION_TOGGLE,
            bunch_id: bunchId,
            channel_id: channelId,
            message_id: messageId,
            emoji: emoji,
          }
          console.log("Sending reaction:", reactionMessage)
          socketRef.current.send(JSON.stringify(reactionMessage))
        } catch (error) {
          console.error("Error sending reaction:", error)
          // should attempt to reconnect
          if (socketRef.current) {
            socketRef.current.close()
            socketRef.current = null
            setIsConnected(false)
          }
        }
      } else {
        console.error("WebSocket not connected")
      }
    },
    [],
  )

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
        pingIntervalRef.current = null
      }
      disconnectWebSocket()
    }
  }, [disconnectWebSocket])

  return (
    <WebSocketContext.Provider
      value={{
        connectWebSocket,
        disconnectWebSocket,
        subscribe,
        unsubscribe,
        sendMessage,
        sendReaction,
        messages,
        isConnected,
        connectionState,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  )
}
