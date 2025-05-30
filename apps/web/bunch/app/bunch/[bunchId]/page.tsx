"use client";

import { ChannelsList } from "@/components/channel/ChannelsList";
import { CreateChannelDialog } from "@/components/channel/CreateChannelDialog";
import { MainLayout } from "@/components/layout/MainLayout";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useBunch } from "@/lib/hooks";
import { Hash, Loader2, Plus, Settings, Users } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function BunchPage() {
  const params = useParams();
  const router = useRouter();
  const bunchId = params?.bunchId as string;
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const { bunch, loading: isLoading, error, fetchBunch } = useBunch(bunchId);

  useEffect(() => {
    if (bunchId) {
      fetchBunch();
    }
  }, [bunchId, fetchBunch]);

  useEffect(() => {
    if (error) {
      console.error("Failed to fetch bunch:", error);
      router.push("/");
    }
  }, [error, router]);

  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </MainLayout>
    );
  }

  if (!bunch) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center h-full p-8">
          <h1 className="text-2xl font-bold mb-4">Bunch not found</h1>
          <p className="text-muted-foreground mb-6">
            The bunch you're looking for doesn't exist or you don't have access
            to it.
          </p>
          <Button onClick={() => router.push("/")}>Go Home</Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="flex flex-col h-full py-2">
        <header
          className="border-b border-border p-4 bg-gradient-to-r from-[var(--bunch-primary-color)]/35 to-25% to-transparent rounded-md"
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
                <p className="text-sm text-muted-foreground">
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
                <Users className="h-4 w-4 mr-2" />
                Members
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/bunch/${bunchId}/settings`)}
              >
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          <div className="w-64 border-r border-border overflow-y-auto">
            {/* Channels sidebar */}
            <div className="flex flex-col h-full">
              <ChannelsList type="text" />
            </div>
          </div>

          <div className="flex-1 p-8 flex flex-col items-center justify-center">
            <Card className="max-w-md w-full">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Hash className="mr-2 h-5 w-5" />
                  Select a Channel
                </CardTitle>
                <CardDescription>
                  Choose a channel from the sidebar or create a new one to start
                  chatting
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  className="w-full"
                  onClick={() => setCreateDialogOpen(true)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Channel
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <CreateChannelDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        bunchId={bunchId}
      />
    </MainLayout>
  );
}
