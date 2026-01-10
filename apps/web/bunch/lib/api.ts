const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchWithAuth(url: string, options: RequestInit = {}, token?: string) {
  const headers = {
    ...options.headers,
    Authorization: token ? `Bearer ${token}` : "",
    "Content-Type": "application/json",
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.message || "An error occurred")
  }

  return response
}

// User API
export const getCurrentUser = async (token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/user/me/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch current user")
  return response.json()
}

export const getUser = async (id: string, token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/user/${id}/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch user")
  return response.json()
}

export const updateUser = async (id: string, data: any, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/user/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to update user")
  return response.json()
}

export const onboardUser = async (data: any, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/user/onboard/`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to onboard user")
  return response.json()
}

// Bunch API
export const getPublicBunches = async (token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/bunch/public/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch public bunches")
  const data = await response.json()
  return data.results
}

export const getBunches = async (token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/bunch/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch bunches")
  const data = await response.json()
  return data.results
}

export const getBunch = async (id: string, token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/bunch/${id}/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch bunch")
  return response.json()
}

export const createBunch = async (data: any, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to create bunch")
  return response.json()
}

export const updateBunch = async (id: string, data: any, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${id}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to update bunch")
  return response.json()
}

export const deleteBunch = async (id: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${id}/`,
    {
      method: "DELETE",
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to delete bunch")
  return response.ok
}

export const joinBunch = async (id: string, inviteCode?: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${id}/join/`,
    {
      method: "POST",
      body: JSON.stringify({ invite_code: inviteCode }),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to join bunch")
  return response.json()
}

export const leaveBunch = async (id: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${id}/leave/`,
    {
      method: "POST",
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to leave bunch")
  return response.ok
}

// Channel API
export const getChannels = async (bunchId: string, token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/bunch/${bunchId}/channels/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch channels")
  const data = await response.json()
  return data.results
}

export const getChannel = async (bunchId: string, channelId: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/channels/${channelId}/`,
    {},
    token,
  )
  if (!response.ok) throw new Error("Failed to fetch channel")
  return response.json()
}

export const createChannel = async (bunchId: string, data: any, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/channels/`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to create channel")
  return response.json()
}

export const updateChannel = async (
  bunchId: string,
  channelId: string,
  data: any,
  token?: string,
) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/channels/${channelId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to update channel")
  return response.json()
}

export const deleteChannel = async (bunchId: string, channelId: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/channels/${channelId}/`,
    {
      method: "DELETE",
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to delete channel")
  return response.ok
}

// Member API
export const getMembers = async (bunchId: string, token?: string) => {
  const response = await fetchWithAuth(`${API_URL}/api/v1/bunch/${bunchId}/members/`, {}, token)
  if (!response.ok) throw new Error("Failed to fetch members")
  const data = await response.json()
  return data.results
}

export const updateMemberRole = async (
  bunchId: string,
  memberId: string,
  role: string,
  token?: string,
) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/members/${memberId}/update_role/`,
    {
      method: "POST",
      body: JSON.stringify({ role }),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to update member role")
  return response.json()
}

export const removeMember = async (bunchId: string, memberId: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/members/${memberId}/`,
    {
      method: "DELETE",
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to remove member")
  return response.ok
}

// Message API
export const getMessages = async (bunchId: string, channelId: string, token?: string) => {
  // Request a larger page size to get more messages initially
  const pageSize = 100
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/messages/?channel=${channelId}&page_size=${pageSize}`,
    {},
    token,
  )
  if (!response.ok) throw new Error("Failed to fetch messages")
  const data = await response.json()

  const transformedMessages = await Promise.all(
    data.results.map(async (message: any) => {
      const authorResponse = await fetchWithAuth(
        `${API_URL}/api/v1/bunch/${bunchId}/members/${message.author_id}/`,
        {},
        token,
      )
      const authorData = await authorResponse.json()
      return {
        id: message.id,
        channel: message.channel_id,
        author: {
          id: authorData.id,
          bunch: bunchId,
          user: {
            id: authorData.user.id,
            username: authorData.user.username,
          },
          role: authorData.role,
          joined_at: authorData.joined_at,
        },
        content: message.content,
        created_at: message.created_at,
        updated_at: message.updated_at,
        edit_count: message.edit_count,
        deleted: message.deleted,
        deleted_at: message.deleted_at,
        reactions: message.reactions || [],
        reaction_counts: message.reaction_counts || {},
        reply_to_id: message.reply_to_id,
        reply_to_preview: message.reply_to_preview,
        reply_count: message.reply_count,
      }
    }),
  )

  return transformedMessages
}

export const createMessage = async (
  bunchId: string,
  channelId: string,
  content: string,
  replyToId?: string,
  token?: string,
) => {
  const requestBody: any = { channel_id: channelId, content }
  if (replyToId) {
    requestBody.reply_to_id = replyToId
  }

  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/messages/`,
    {
      method: "POST",
      body: JSON.stringify(requestBody),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to create message")
  return response.json()
}

export const updateMessage = async (
  bunchId: string,
  messageId: string,
  content: string,
  token?: string,
) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/messages/${messageId}/`,
    {
      method: "PATCH",
      body: JSON.stringify({ content }),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to update message")
  return response.json()
}

export const deleteMessage = async (bunchId: string, messageId: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/messages/${messageId}/`,
    {
      method: "DELETE",
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to delete message")
  return response.ok
}

// Reaction API
export const getReactions = async (bunchId: string, messageId?: string, token?: string) => {
  const queryParams = messageId ? `?message=${messageId}` : ""
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/reactions/${queryParams}`,
    {},
    token,
  )
  if (!response.ok) throw new Error("Failed to fetch reactions")
  const data = await response.json()
  return data.results
}

export const createReaction = async (
  bunchId: string,
  messageId: string,
  emoji: string,
  token?: string,
) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/reactions/`,
    {
      method: "POST",
      body: JSON.stringify({ message_id: messageId, emoji }),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to create reaction")
  return response.json()
}

export const deleteReaction = async (bunchId: string, reactionId: string, token?: string) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/reactions/${reactionId}/`,
    {
      method: "DELETE",
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to delete reaction")
  return response.ok
}

export const toggleReaction = async (
  bunchId: string,
  messageId: string,
  emoji: string,
  token?: string,
) => {
  const response = await fetchWithAuth(
    `${API_URL}/api/v1/bunch/${bunchId}/reactions/toggle/`,
    {
      method: "POST",
      body: JSON.stringify({ message_id: messageId, emoji }),
    },
    token,
  )
  if (!response.ok) throw new Error("Failed to toggle reaction")
  return response.json()
}
