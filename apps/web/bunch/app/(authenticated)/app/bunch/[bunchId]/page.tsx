"use client"

import { ChannelsList } from "@/components/channel/ChannelsList"
import { CreateChannelButton } from "@/components/channel/CreateChannelButton"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useBunch } from "@/lib/hooks"
import { Hash, Loader2, Plus, Settings, Users } from "lucide-react"
import { useParams, useRouter } from "next/navigation"
import { useEffect } from "react"

export default function BunchPage() {
  const params = useParams()
  const router = useRouter()
  const bunchId = params.bunchId as string

  const { bunch, loading: isLoading, error, fetchBunch } = useBunch(bunchId)

  useEffect(() => {
    if (bunchId) {
      fetchBunch()
    }
  }, [bunchId, fetchBunch])

  useEffect(() => {
    if (error) {
      console.error("Failed to fetch bunch:", error)
      router.push("/")
    }
  }, [error, router])

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="text-primary h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (!bunch) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8">
        <h1 className="mb-4 text-2xl font-bold">Bunch not found</h1>
        <p className="text-muted-foreground mb-6">
          The bunch you're looking for doesn't exist or you don't have access to it.
        </p>
        <Button onClick={() => router.push("/")}>Go Home</Button>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col py-2">
      <header
        className="border-border rounded-md border-b bg-linear-to-r from-(--bunch-primary-color)/35 to-transparent to-25% p-4"
        style={
          {
            "--bunch-primary-color": bunch?.primary_color,
          } as React.CSSProperties
        }
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Avatar className="h-12 w-12">
              {bunch.icon ? (
                <AvatarImage src={bunch.icon} alt={bunch.name} />
              ) : (
                <AvatarFallback className="bg-primary/50 text-primary-foreground">
                  {bunch.name.substring(0, 2)}
                </AvatarFallback>
              )}
            </Avatar>
            <div>
              <h1 className="text-xl font-bold">{bunch.name}</h1>
              <p className="text-muted-foreground text-sm">
                {bunch.description || "No description"}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push(`/bunch/${bunchId}/members`)}
            >
              <Users className="mr-2 h-4 w-4" />
              Members
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push(`/bunch/${bunchId}/settings`)}
            >
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="border-border w-64 overflow-y-auto border-r">
          {/* Channels sidebar */}
          <div className="flex h-full flex-col">
            <ChannelsList type="text" />
          </div>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Hash className="mr-2 h-5 w-5" />
                Select a Channel
              </CardTitle>
              <CardDescription>
                Choose a channel from the sidebar or create a new one to start chatting
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CreateChannelButton bunchId={bunchId}>
                <Button className="w-full">
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Channel
                </Button>
              </CreateChannelButton>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
