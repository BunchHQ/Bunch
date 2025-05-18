"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import {
  PlusCircle,
  Settings,
  User,
  Menu,
  X,
  Hash,
  Volume2,
  Bell,
  MessageCircle,
  Plus,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bunch } from "@/lib/types";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UserNav } from "@/components/user/UserNav";
import { CreateBunchDialog } from "@/components/bunch/CreateBunchDialog";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "../theme/ThemeToggle";
import { UserButton } from "@clerk/nextjs";
import { UserProfile } from "@clerk/clerk-react";

interface SidebarProps {
  bunches: Bunch[];
}

export function Sidebar({ bunches }: SidebarProps) {
  const params = useParams();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const currentBunchId = params?.bunchId as string;

  // Get the current bunch if there's an ID in the params
  const currentBunch = bunches?.find((bunch) => bunch.id === currentBunchId);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <div className="fixed top-4 left-4 z-40 md:hidden">
        <Button variant="ghost" size="icon" onClick={toggleSidebar}>
          {isOpen ? <X /> : <Menu />}
        </Button>
      </div>

      <div
        className={cn(
          "fixed inset-y-0 left-0 z-30 flex flex-col bg-card border-1 border-border transition-transform duration-300 ease-in-out",
          "w-15 rounded-lg m-2",
          isOpen ? "translate-x-0" : "translate-x-[-100%]",
          "md:relative md:translate-x-0 md:items-center"
        )}
      >
        <div className="flex-none p-2 flex flex-col items-center gap-2 overflow-y-auto">
          <ScrollArea className="flex-1 w-full flex flex-col items-center space-y-2">
            {bunches.map((bunch) => (
              <TooltipProvider key={bunch.id}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Link
                      href={`/bunch/${bunch.id}`}
                      className="w-12 h-12 rounded-[100px] flex items-center justify-center bg-card hover:!bg-secondary hover:rounded-[15px] transition-all"
                    >
                      <Avatar className="h-12 w-12">
                        {bunch.icon ? (
                          <AvatarImage src={bunch.icon} alt={bunch.name} />
                        ) : (
                          <AvatarFallback
                            className={cn(
                              "bg-secondary text-primary/50 text-lg",
                              currentBunchId === bunch.id &&
                                "bg-secondary text-primary"
                            )}
                          >
                            {bunch.name.substring(0, 2)}
                          </AvatarFallback>
                        )}
                      </Avatar>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p>{bunch.name}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ))}
          </ScrollArea>
        </div>

        <div className="flex-none p-2 mt-auto w-full flex flex-col items-center gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                  onClick={() => setCreateDialogOpen(true)}
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-full h-full p-0 bg-primary/10 opacity-60 rounded-[100px] hover:!bg-primary/20 hover:rounded-[15px] transition-all"
                  >
                    <Plus className="!h-6 !w-6" />
                  </Button>
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Start a new bunch</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="w-12 h-12 flex items-center justify-center bg-primary/10 opacity-60 rounded-[100px] hover:!bg-primary/20 hover:rounded-[15px] transition-all">
                  <ThemeToggle />
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Toggle Theme</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/messages"
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-full h-full p-0 bg-primary/10 opacity-60 rounded-[100px] hover:!bg-primary/20 hover:rounded-[15px] transition-all"
                  >
                    <MessageCircle className="!h-5 !w-5" />
                  </Button>
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Direct Messages</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/settings"
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-full h-full p-0 bg-primary/10 opacity-60 rounded-[100px] hover:!bg-primary/20 hover:rounded-[15px] transition-all"
                  >
                    <Settings className="!h-5 !w-5" />
                  </Button>
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Settings</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="w-12 h-12 rounded-full flex items-center justify-center bg-primary/5 hover:bg-primary/60 transition-colors">
                  <UserButton
                    appearance={{
                      elements: { userButtonAvatarBox: "w-12 h-12 rounded-md" },
                    }}
                  />
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Profile</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>

      <CreateBunchDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </>
  );
}
