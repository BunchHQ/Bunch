"use client"

import { ChannelsList } from "@/components/channel/ChannelsList"
import { MessageList } from "@/components/message/MessageList"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useBunch, useChannels } from "@/lib/hooks"
import type { Channel } from "@/lib/types"
import { Bell, Hash, Info, Users, Volume2 } from "lucide-react"
import { useParams, useRouter } from "next/navigation"
import { useEffect } from "react"

export default function ChannelPage() {
  const params = useParams()
  const router = useRouter()
  const bunchId = params?.bunchId as string
  const channelId = params?.channelId as string

  const { bunch, loading: isBunchLoading, error: bunchError, fetchBunch } = useBunch(bunchId)
  const {
    channels,
    loading: isChannelsLoading,
    error: channelsError,
    fetchChannels,
  } = useChannels(bunchId)

  useEffect(() => {
    if (bunchId && channelId) {
      fetchBunch()
      fetchChannels()
    }
  }, [bunchId, channelId, fetchBunch, fetchChannels])

  useEffect(() => {
    if (bunchError || channelsError) {
      console.error("Failed to fetch data:", bunchError || channelsError)
      router.push("/")
    }
  }, [bunchError, channelsError, router])

  const getChannelIcon = (channelType?: string) => {
    switch (channelType) {
      case "text":
        return <Hash className="h-5 w-5" />
      case "voice":
        return <Volume2 className="h-5 w-5" />
      case "announcement":
        return <Bell className="h-5 w-5" />
      default:
        return <Hash className="h-5 w-5" />
    }
  }

  const isLoading = isBunchLoading || isChannelsLoading
  const channel = channels?.find((c: Channel) => c.id === channelId)

  if (!isLoading && !bunch) {
    return <h1>Bunch not found</h1>
  }

  return (
    <div className="flex h-full flex-col pt-2">
      <header
        className="border-border rounded-md border-b bg-linear-to-r from-(--bunch-primary-color)/35 to-transparent to-25% p-4"
        style={
          {
            "--bunch-primary-color": bunch?.primary_color,
          } as React.CSSProperties
        }
      >
        {isLoading ? (
          <div className="flex items-center space-x-4">
            <Skeleton className="h-6 w-6 rounded-full" />
            <Skeleton className="h-5 w-40" />
            <div className="ml-auto flex space-x-2">
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-8 w-20" />
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex min-w-62.5 items-center space-x-2">
                <Avatar className="h-12 w-12">
                  {bunch?.icon ? (
                    <AvatarImage src={bunch.icon} alt={bunch.name} />
                  ) : (
                    <AvatarFallback className="bg-primary/50 text-primary-foreground">
                      {bunch?.name.substring(0, 2)}
                    </AvatarFallback>
                  )}
                </Avatar>
                <div>
                  <h1 className="text-xl font-bold">{bunch?.name}</h1>
                  <p className="text-muted-foreground text-sm">
                    {bunch?.description || "No description"}
                  </p>
                </div>
              </div>
              {getChannelIcon(channel?.type)}
              <h1 className="text-xl font-medium">{channel?.name}</h1>
              {channel?.description && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Info className="text-muted-foreground h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{channel.description}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
              <Separator orientation="vertical" className="mx-2 h-6" />
              <span className="text-muted-foreground text-sm">
                {channel?.type === "text"
                  ? "Text Channel"
                  : channel?.type === "voice"
                    ? "Voice Channel"
                    : "Announcement Channel"}
              </span>
            </div>
            <div className="flex items-center">
              <Button variant="ghost" size="sm">
                <Users className="mr-2 h-4 w-4" />
                Members
              </Button>
            </div>
          </div>
        )}
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="border-border w-64 overflow-y-auto border-r">
          <ChannelsList type={(channel?.type as "text" | "voice" | "announcement") || "text"} />
        </div>

        <div className="flex flex-1 flex-col">
          <MessageList />
        </div>
      </div>
    </div>
  )
}
