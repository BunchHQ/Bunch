"use client";

import { CreateBunchDialog } from "@/components/bunch/CreateBunchDialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { Bunch } from "@/lib/types";
import { cn } from "@/lib/utils";
import { UserButton } from "@clerk/nextjs";
import {
  Globe2Icon,
  Menu,
  MessageCircle,
  Plus,
  Settings,
  X,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { ThemeToggle } from "../theme/ThemeToggle";

interface SidebarProps {
  bunches: Bunch[];
}

export function Sidebar({ bunches }: SidebarProps) {
  const params = useParams();
  // const pathname = usePathname();
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
        {" "}
        <Button variant="ghost" size="icon" onClick={toggleSidebar}>
          {isOpen ? <X /> : <Menu />}
        </Button>
        <span className="sr-only">Toggle Sidebar</span>
      </div>
      <nav
        className={cn(
          "fixed inset-y-0 left-0 z-30 flex flex-col bg-card border-1 border-border transition-transform duration-300 ease-in-out",
          "w-15 rounded-lg m-2",
          isOpen ? "translate-x-0" : "translate-x-[-100%]",
          "md:relative md:translate-x-0 md:items-center",
          "flex flex-col h-[calc(100vh-1rem)]" // Ensure it takes full height minus margin
        )}
      >
        <div className="flex-grow overflow-hidden">
          <div className="h-full overflow-y-auto scrollbar-hide p-2 flex flex-col items-center">
            <div className="flex flex-col items-center space-y-2 flex-grow">
              {bunches.map((bunch) => (
                <TooltipProvider key={bunch.id}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Link
                        href={`/bunch/${bunch.id}`}
                        className="w-12 h-12 rounded-[100px] flex items-center justify-center bg-[var(--bunch-primary-color)]/20  hover:rounded-[15px] transition-all"
                        style={
                          {
                            "--bunch-primary-color": bunch?.primary_color,
                          } as React.CSSProperties
                        }
                      >
                        <Avatar className="h-12 w-12">
                          {bunch.icon ? (
                            <AvatarImage src={bunch.icon} alt={bunch.name} />
                          ) : (
                            <AvatarFallback
                              className={cn(
                                "bg-transparent text-[var(--bunch-primary-color)] text-lg",
                                currentBunchId === bunch.id && "text-primary"
                              )}
                              style={
                                {
                                  "--bunch-primary-color": bunch?.primary_color,
                                } as React.CSSProperties
                              }
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
            </div>

            <div className="flex flex-col items-center gap-2 mt-4">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    {/* biome-ignore lint/a11y/useKeyWithClickEvents: <explanation> */}
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
                        <span className="sr-only">Create Bunch</span>
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
                    <Link
                      href="/browse"
                      className="w-12 h-12 rounded-full flex items-center justify-center"
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        className="w-full h-full p-0 bg-primary/10 opacity-60 rounded-[100px] hover:!bg-primary/20 hover:rounded-[15px] transition-all"
                      >
                        <Globe2Icon className="!h-5 !w-5" />
                      </Button>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p>Browse Public Bunches</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>{" "}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="w-12 h-12 flex items-center justify-center">
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
                  </TooltipContent>{" "}
                </Tooltip>
              </TooltipProvider>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="w-12 h-12 rounded-full flex items-center justify-center bg-primary/5 hover:bg-primary/60 transition-colors">
                      <UserButton
                        appearance={{
                          elements: {
                            userButtonAvatarBox: "w-12 h-12 rounded-md",
                          },
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
        </div>
      </nav>
      <CreateBunchDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </>
  );
}
