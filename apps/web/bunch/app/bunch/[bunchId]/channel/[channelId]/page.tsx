"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/MainLayout";
import { Users, Info, Hash, Volume2, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChannelsList } from "@/components/channel/ChannelsList";
import { MessageList } from "@/components/message/MessageList";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useBunch, useChannels } from "@/lib/hooks";
import { Channel } from "@/lib/types";

export default function ChannelPage() {
  const params = useParams();
  const router = useRouter();
  const bunchId = params?.bunchId as string;
  const channelId = params?.channelId as string;

  const {
    bunch,
    loading: isBunchLoading,
    error: bunchError,
    fetchBunch,
  } = useBunch(bunchId);
  const {
    channels,
    loading: isChannelsLoading,
    error: channelsError,
    fetchChannels,
  } = useChannels(bunchId);

  useEffect(() => {
    if (bunchId && channelId) {
      fetchBunch();
      fetchChannels();
    }
  }, [bunchId, channelId, fetchBunch, fetchChannels]);

  useEffect(() => {
    if (bunchError || channelsError) {
      console.error("Failed to fetch data:", bunchError || channelsError);
      router.push("/");
    }
  }, [bunchError, channelsError, router]);

  const getChannelIcon = (channelType?: string) => {
    switch (channelType) {
      case "text":
        return <Hash className="h-5 w-5" />;
      case "voice":
        return <Volume2 className="h-5 w-5" />;
      case "announcement":
        return <Bell className="h-5 w-5" />;
      default:
        return <Hash className="h-5 w-5" />;
    }
  };

  const isLoading = isBunchLoading || isChannelsLoading;
  const channel = channels?.find((c: Channel) => c.id === channelId);

  return (
    <MainLayout>
      <div className="flex flex-col h-full">
        <header className="border-b border-border p-4">
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
                {getChannelIcon(channel?.type)}
                <h1 className="text-xl font-medium">{channel?.name}</h1>
                {channel?.description && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Info className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{channel.description}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
                <Separator orientation="vertical" className="h-6 mx-2" />
                <span className="text-sm text-muted-foreground">
                  {channel?.type === "text"
                    ? "Text Channel"
                    : channel?.type === "voice"
                    ? "Voice Channel"
                    : "Announcement Channel"}
                </span>
              </div>
              <div className="flex items-center">
                <Button variant="ghost" size="sm">
                  <Users className="h-4 w-4 mr-2" />
                  Members
                </Button>
              </div>
            </div>
          )}
        </header>

        <div className="flex flex-1 overflow-hidden">
          <div className="w-64 border-r border-border overflow-y-auto">
            <ChannelsList
              type={
                (channel?.type as "text" | "voice" | "announcement") || "text"
              }
            />
          </div>

          <div className="flex-1 flex flex-col">
            <MessageList />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
