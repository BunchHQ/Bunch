"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Hash,
  Volume2,
  Bell,
  Lock,
  Plus,
  Settings,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Channel } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CreateChannelDialog } from "./CreateChannelDialog";
import { useChannels } from "@/lib/hooks";

interface ChannelsListProps {
  type: "text" | "voice" | "announcement";
}

export function ChannelsList({ type }: ChannelsListProps) {
  const params = useParams();
  const bunchId = params?.bunchId as string;
  const currentChannelId = params?.channelId as string;

  const { channels, loading: isLoading, fetchChannels } = useChannels(bunchId);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  useEffect(() => {
    if (bunchId) {
      fetchChannels();
    }
  }, [bunchId, fetchChannels]);

  const getChannelIcon = (channelType: string) => {
    switch (channelType) {
      case "text":
        return <Hash className="h-4 w-4 flex-shrink-0" />;
      case "voice":
        return <Volume2 className="h-4 w-4 flex-shrink-0" />;
      case "announcement":
        return <Bell className="h-4 w-4 flex-shrink-0" />;
      default:
        return <Hash className="h-4 w-4 flex-shrink-0" />;
    }
  };

  const getTypeName = (channelType: string) => {
    switch (channelType) {
      case "text":
        return "TEXT CHANNELS";
      case "voice":
        return "VOICE CHANNELS";
      case "announcement":
        return "ANNOUNCEMENTS";
      default:
        return "CHANNELS";
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
        <p className="text-sm text-muted-foreground">Loading channels...</p>
      </div>
    );
  }

  const filteredChannels = channels?.filter((channel) => channel.type === type);

  return (
    <>
      <div className="px-2 pt-4">
        <div className="flex items-center justify-between px-2 mb-2">
          <h3 className="text-xs font-semibold text-muted-foreground">
            {getTypeName(type)}
          </h3>
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
          <div className="flex flex-col items-center justify-center py-8 px-2 text-center">
            <p className="text-sm text-muted-foreground mb-4">
              No {type} channels yet
            </p>
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => setCreateDialogOpen(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Create a channel
            </Button>
          </div>
        ) : (
          <ScrollArea className="h-[calc(100vh-200px)]">
            <div className="space-y-1 px-1">
              {filteredChannels
                ?.sort((a, b) => a.position - b.position)
                .map((channel) => (
                  <Link
                    key={channel.id}
                    href={`/bunch/${bunchId}/channel/${channel.id}`}
                  >
                    <div
                      className={cn(
                        "flex items-center justify-between group px-2 py-1.5 rounded-md hover:bg-accent/50 transition-colors",
                        currentChannelId === channel.id && "bg-accent"
                      )}
                    >
                      <div className="flex items-center gap-2 truncate">
                        {getChannelIcon(channel.type)}
                        <span className="truncate text-sm">{channel.name}</span>
                        {channel.is_private && (
                          <Lock className="h-3 w-3 text-muted-foreground" />
                        )}
                      </div>

                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
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

      <CreateChannelDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        bunchId={bunchId}
        defaultType={type}
        onSuccess={(newChannel) => {
          if (newChannel.type === type) {
            fetchChannels();
          }
        }}
      />
    </>
  );
}
