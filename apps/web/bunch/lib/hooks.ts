import { useAuth } from "@clerk/nextjs"
import { useCallback, useState } from "react"
import * as api from "./api"
import type { Bunch, Channel, Message, User } from "./types"

// User hooks
export const useCurrentUser = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { getToken } = useAuth()

  const fetchUser = useCallback(async () => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.getCurrentUser(token)
      setUser(data)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken])

  return { user, loading, error, fetchUser }
}

// Bunch hooks
export const useBunches = (fetchPublic?: boolean) => {
  const [bunches, setBunches] = useState<Bunch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { getToken } = useAuth()

  const fetchBunches = useCallback(async () => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      let data = null

      if (fetchPublic) {
        // no auth for public bunches
        data = await api.getPublicBunches(token || undefined)
      } else {
        if (!token) {
          throw new Error("No authentication token available")
        }

        data = await api.getBunches(token)
      }

      setBunches(data)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [getToken, fetchPublic])

  const createBunch = useCallback(
    async (data: Partial<Bunch>) => {
      try {
        const token = await getToken({ template: "Django" })
        if (!token) {
          throw new Error("No authentication token available")
        }
        const newBunch = await api.createBunch(data, token)
        setBunches(prev => [...prev, newBunch])
        return newBunch
      } catch (err) {
        setError(err as Error)
        throw err
      }
    },
    [getToken],
  )

  return { bunches, loading, error, fetchBunches, createBunch }
}

// Channel hooks
export const useChannels = (bunchId: string) => {
  const [channels, setChannels] = useState<Channel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { getToken } = useAuth()

  const fetchChannels = useCallback(async () => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.getChannels(bunchId, token)
      setChannels(data)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [bunchId, getToken])

  const createChannel = useCallback(
    async (data: Partial<Channel>) => {
      try {
        const token = await getToken({ template: "Django" })
        if (!token) {
          throw new Error("No authentication token available")
        }
        const newChannel = await api.createChannel(bunchId, data, token)
        setChannels(prev => [...prev, newChannel])
        return newChannel
      } catch (err) {
        setError(err as Error)
        throw err
      }
    },
    [bunchId, getToken],
  )

  return { channels, loading, error, fetchChannels, createChannel }
}

// Message hooks
export function useMessages(bunchId: string, channelId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const { getToken } = useAuth()

  const fetchMessages = async () => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.getMessages(bunchId, channelId, token)
      setMessages(data)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }
  const sendMessage = async (content: string, replyToId?: string) => {
    try {
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.createMessage(
        bunchId,
        channelId,
        content,
        replyToId,
        token,
      )
      setMessages(prev => [...prev, data])
      return data
    } catch (err) {
      setError(err as Error)
      throw err
    }
  }

  const updateMessage = async (messageId: string, content: string) => {
    try {
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.updateMessage(bunchId, messageId, content, token)
      setMessages(prev => prev.map(msg => (msg.id === messageId ? data : msg)))
      return data
    } catch (err) {
      setError(err as Error)
      throw err
    }
  }

  const deleteMessage = async (messageId: string) => {
    try {
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      await api.deleteMessage(bunchId, messageId, token)
      setMessages(prev => prev.filter(msg => msg.id !== messageId))
    } catch (err) {
      setError(err as Error)
      throw err
    }
  }
  return {
    messages,
    loading,
    error,
    fetchMessages,
    sendMessage,
    updateMessage,
    deleteMessage,
    setMessages,
  }
}

// reaction hooks (useless)
export function useReactions(bunchId: string) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const { getToken } = useAuth()

  const toggleReaction = async (messageId: string, emoji: string) => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.toggleReaction(bunchId, messageId, emoji, token)
      setError(null)
      return data
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const createReaction = async (messageId: string, emoji: string) => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.createReaction(bunchId, messageId, emoji, token)
      setError(null)
      return data
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteReaction = async (reactionId: string) => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      await api.deleteReaction(bunchId, reactionId, token)
      setError(null)
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    toggleReaction,
    createReaction,
    deleteReaction,
  }
}

// THE reaction hooks
export function useWebSocketReactions() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const toggleReaction = async (
    bunchId: string,
    channelId: string,
    messageId: string,
    emoji: string,
    sendReaction: (
      bunchId: string,
      channelId: string,
      messageId: string,
      emoji: string,
    ) => void,
  ) => {
    try {
      setLoading(true)
      sendReaction(bunchId, channelId, messageId, emoji)
      setError(null)
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    toggleReaction,
  }
}

export const useBunch = (bunchId: string) => {
  const [bunch, setBunch] = useState<Bunch | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { getToken } = useAuth()

  const fetchBunch = useCallback(async () => {
    try {
      setLoading(true)
      const token = await getToken({ template: "Django" })
      if (!token) {
        throw new Error("No authentication token available")
      }
      const data = await api.getBunch(bunchId, token)
      setBunch(data)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [bunchId, getToken])

  return { bunch, loading, error, fetchBunch }
}
