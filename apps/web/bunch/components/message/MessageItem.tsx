"use client";

import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Message } from "@/lib/types";
import { MoreHorizontal, Edit, Trash, Reply } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { MessageEditor } from "./MessageEditor";
import { useAuth } from "@clerk/nextjs";
import { useMessages } from "@/lib/hooks";

interface MessageItemProps {
  message: Message;
  showHeader: boolean;
  bunchId: string;
}

export function MessageItem({
  message,
  showHeader,
  bunchId,
}: MessageItemProps) {
  const { userId } = useAuth();
  const { updateMessage, deleteMessage } = useMessages(
    bunchId,
    message.channel
  );
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Format timestamp
  const timestamp = new Date(message.created_at);
  const formattedTime = timestamp.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const formattedDate = timestamp.toLocaleDateString();
  const timeAgo = formatDistanceToNow(timestamp, { addSuffix: true });

  const isAuthor = userId === message.author.user.id; // won't work clerk userId doesn't match user.id

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSaveEdit = async (content: string) => {
    try {
      await updateMessage(message.id, content);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to update message:", error);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteMessage(message.id);
    } catch (error) {
      console.error("Failed to delete message:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (message.deleted) {
    return (
      <div className="px-4 py-2 opacity-60">
        {showHeader && (
          <div className="flex items-start space-x-2 mb-1.5">
            <Avatar className="h-8 w-8">
              <AvatarImage
                src={message.author.user.avatar || undefined}
                alt={message.author.user.username}
              />
              <AvatarFallback className="bg-primary/10 text-primary-foreground">
                {message.author.user.username.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-baseline">
                <span className="font-medium mr-2">
                  {message.author.nickname || message.author.user.username}
                </span>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="text-xs text-muted-foreground">
                        {formattedTime}
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>
                        {formattedDate} ({timeAgo})
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>
          </div>
        )}
        <div className="pl-10 italic text-muted-foreground text-sm">
          This message was deleted
        </div>
      </div>
    );
  }

  return (
    <div className="group px-4 py-2 hover:bg-accent/50 rounded-md transition-colors relative">
      {showHeader ? (
        <div className="flex items-start space-x-2 mb-1.5">
          <Avatar className="h-8 w-8">
            <AvatarImage
              src={message.author.user.avatar || undefined}
              alt={message.author.user.username}
            />
            <AvatarFallback className="bg-primary text-primary-foreground">
              {message.author.user.username.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div>
            <div className="flex items-baseline">
              <span className="font-medium mr-2">
                {message.author.nickname || message.author.user.username}
              </span>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className="text-xs text-muted-foreground">
                      {formattedTime}
                    </span>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>
                      {formattedDate} ({timeAgo})
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
        </div>
      ) : (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="absolute left-2 top-1/2 transform -translate-y-1/2 text-[9px] font-medium text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity z-10">
                {formattedTime}
              </span>
            </TooltipTrigger>
            <TooltipContent>
              <p>
                {formattedDate} ({timeAgo})
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      <div className={`${showHeader ? "ml-10" : "ml-10"} break-words`}>
        {isEditing ? (
          <MessageEditor
            initialContent={message.content}
            onSave={handleSaveEdit}
            onCancel={handleCancelEdit}
          />
        ) : (
          <>
            <div className="text-sm whitespace-pre-wrap">{message.content}</div>
            {message.edit_count > 0 && (
              <span className="text-xs text-muted-foreground italic">
                (edited)
              </span>
            )}
          </>
        )}
      </div>

      {/* {!isEditing && (
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Reply className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Reply</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {isAuthor && (
            <DropdownMenu>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>More actions</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleEdit}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Message
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash className="h-4 w-4 mr-2" />
                  Delete Message
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      )} */}
    </div>
  );
}
