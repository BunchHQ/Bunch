"use client"

import { useCallback, useState } from "react"
import * as api from "./api"
import type { Bunch, Channel, Message, User } from "./types"
import { createClient } from "./supabase/client"

// User hooks
export const useCurrentUser = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const supabase = createClient()

  const fetchUser = useCallback(async () => {
    try {
      setLoading(true)
      await supabase.auth.getUser()

      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError
      }

      const userData = await api.getCurrentUser(session.access_token)
      setUser(userData)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [supabase])

  const onboardUser = useCallback(
    async (data: Partial<User>) => {
      try {
        setLoading(true)

        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession()
        if (sessionError || !session) {
          throw sessionError
        }
        const onboardData = await api.onboardUser(data, session?.access_token)
        await fetchUser()
        return onboardData
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    },
    [supabase],
  )

  return { user, loading, error, fetchUser, onboardUser }
}

// Bunch hooks
export const useBunches = (fetchPublic: boolean = false) => {
  const [bunches, setBunches] = useState<Bunch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const supabase = createClient()

  const fetchBunches = useCallback(async () => {
    try {
      setLoading(true)
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      let bunchData = null

      if (fetchPublic) {
        // no auth for public bunches
        bunchData = await api.getPublicBunches(session?.access_token || undefined)
      } else {
        if (sessionError || !session) {
          throw sessionError || new Error("No authentication token available")
        }

        bunchData = await api.getBunches(session.access_token)
      }

      setBunches(bunchData)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [supabase, fetchPublic])

  const createBunch = useCallback(
    async (data: Partial<Bunch>) => {
      try {
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession()
        if (sessionError || !session) {
          throw sessionError || new Error("No authentication token available")
        }

        const newBunch = await api.createBunch(data, session.access_token)
        setBunches(prev => [...prev, newBunch])
        return newBunch
      } catch (err) {
        setError(err as Error)
        throw err
      }
    },
    [supabase],
  )

  return { bunches, loading, error, fetchBunches, createBunch }
}

// Channel hooks
export const useChannels = (bunchId: string) => {
  const [channels, setChannels] = useState<Channel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const supabase = createClient()

  const fetchChannels = useCallback(async () => {
    try {
      setLoading(true)
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const channelsData = await api.getChannels(bunchId, session.access_token)
      setChannels(channelsData)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [bunchId, supabase])

  const createChannel = useCallback(
    async (data: Partial<Channel>) => {
      try {
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession()
        if (sessionError || !session) {
          throw sessionError || new Error("No authentication token available")
        }

        const newChannel = await api.createChannel(bunchId, data, session.access_token)
        setChannels(prev => [...prev, newChannel])
        return newChannel
      } catch (err) {
        setError(err as Error)
        throw err
      }
    },
    [bunchId, supabase],
  )

  return { channels, loading, error, fetchChannels, createChannel }
}

// Message hooks
export function useMessages(bunchId: string, channelId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const supabase = createClient()

  const fetchMessages = async () => {
    try {
      setLoading(true)
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const messagesData = await api.getMessages(bunchId, channelId, session.access_token)
      setMessages(messagesData)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }
  const sendMessage = async (content: string, replyToId?: string) => {
    try {
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const newMessage = await api.createMessage(
        bunchId,
        channelId,
        content,
        replyToId,
        session.access_token,
      )
      setMessages(prev => [...prev, newMessage])
      return newMessage
    } catch (err) {
      setError(err as Error)
      throw err
    }
  }

  const updateMessage = async (messageId: string, content: string) => {
    try {
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const updatedMessage = await api.updateMessage(
        bunchId,
        messageId,
        content,
        session.access_token,
      )
      setMessages(prev => prev.map(msg => (msg.id === messageId ? updatedMessage : msg)))
      return updatedMessage
    } catch (err) {
      setError(err as Error)
      throw err
    }
  }

  const deleteMessage = async (messageId: string) => {
    try {
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      await api.deleteMessage(bunchId, messageId, session.access_token)
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

// reaction hooks (unused)
export function useReactions(bunchId: string) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const supabase = createClient()

  const toggleReaction = async (messageId: string, emoji: string) => {
    try {
      setLoading(true)
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const reactionData = await api.toggleReaction(bunchId, messageId, emoji, session.access_token)
      setError(null)
      return reactionData
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
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const reactionData = await api.createReaction(bunchId, messageId, emoji, session.access_token)
      setError(null)
      return reactionData
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
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      await api.deleteReaction(bunchId, reactionId, session.access_token)
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
    sendReaction: (bunchId: string, channelId: string, messageId: string, emoji: string) => void,
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
  const supabase = createClient()

  const fetchBunch = useCallback(async () => {
    try {
      setLoading(true)
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw sessionError || new Error("No authentication token available")
      }

      const bunchData = await api.getBunch(bunchId, session.access_token)
      setBunch(bunchData)
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [bunchId, supabase])

  return { bunch, loading, error, fetchBunch }
}
