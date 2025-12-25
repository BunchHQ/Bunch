"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useChannels } from "@/lib/hooks"
import { cn } from "@/lib/utils"
import { Bell, Hash, Loader2, Lock, Plus, Settings, Volume2 } from "lucide-react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { useEffect, useState } from "react"
import { CreateChannelButton } from "./CreateChannelButton"

interface ChannelsListProps {
  type: "text" | "voice" | "announcement"
}

export function ChannelsList({ type }: ChannelsListProps) {
  const params = useParams()
  const bunchId = params?.bunchId as string
  const currentChannelId = params?.channelId as string

  const { channels, loading: isLoading, fetchChannels } = useChannels(bunchId)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  useEffect(() => {
    if (bunchId) {
      fetchChannels()
    }
  }, [bunchId, fetchChannels])

  const getChannelIcon = (channelType: string) => {
    switch (channelType) {
      case "text":
        return <Hash className="h-4 w-4 shrink-0" />
      case "voice":
        return <Volume2 className="h-4 w-4 shrink-0" />
      case "announcement":
        return <Bell className="h-4 w-4 shrink-0" />
      default:
        return <Hash className="h-4 w-4 shrink-0" />
    }
  }

  const getTypeName = (channelType: string) => {
    switch (channelType) {
      case "text":
        return "TEXT CHANNELS"
      case "voice":
        return "VOICE CHANNELS"
      case "announcement":
        return "ANNOUNCEMENTS"
      default:
        return "CHANNELS"
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-4">
        <Loader2 className="text-primary mb-2 h-8 w-8 animate-spin" />
        <p className="text-muted-foreground text-sm">Loading channels...</p>
      </div>
    )
  }

  const filteredChannels = channels?.filter(channel => channel.type === type)

  return (
    <>
      <div className="px-2 pt-4">
        <div className="mb-2 flex items-center justify-between px-2">
          <h3 className="text-muted-foreground text-xs font-semibold">{getTypeName(type)}</h3>
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5"
            onClick={() => setCreateDialogOpen(true)}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {filteredChannels?.length === 0 ? (
          <div className="flex flex-col items-center justify-center px-2 py-8 text-center">
            <p className="text-muted-foreground mb-4 text-sm">No {type} channels yet</p>
            <CreateChannelButton
              bunchId={bunchId}
              defaultType={type}
              onSuccess={newChannel => {
                if (newChannel.type === type) {
                  fetchChannels()
                }
              }}
            >
              <Button variant="outline" size="sm" className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Create a channel
              </Button>
            </CreateChannelButton>
          </div>
        ) : (
          <ScrollArea className="h-[calc(100vh-200px)]">
            <div className="space-y-1 px-1">
              {filteredChannels
                ?.sort((a, b) => a.position - b.position)
                .map(channel => (
                  <Link key={channel.id} href={`/app/bunch/${bunchId}/channel/${channel.id}`}>
                    <div
                      className={cn(
                        "group hover:bg-accent/50 flex items-center justify-between rounded-md px-2 py-1.5 transition-colors",
                        currentChannelId === channel.id && "bg-accent",
                      )}
                    >
                      <div className="flex items-center gap-2 truncate">
                        {getChannelIcon(channel.type)}
                        <span className="truncate text-sm">{channel.name}</span>
                        {channel.is_private && <Lock className="text-muted-foreground h-3 w-3" />}
                      </div>

                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 transition-opacity group-hover:opacity-100"
                      >
                        <Settings className="h-3 w-3" />
                      </Button>
                    </div>
                  </Link>
                ))}
            </div>
          </ScrollArea>
        )}
      </div>
    </>
  )
}
