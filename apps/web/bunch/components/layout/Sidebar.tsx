"use client"

import { UserButton } from "@/components/auth/UserButton"
import { CreateBunchButton } from "@/components/bunch/CreateBunchButton"
import { ThemeToggle } from "@/components/theme/ThemeToggle"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useBunches } from "@/lib/hooks"
import { cn } from "@/lib/utils"
import { Globe2Icon, Menu, MessageCircle, Plus, Settings, X } from "lucide-react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { useEffect, useState } from "react"

export function Sidebar() {
  const { bunches, loading, fetchBunches, error } = useBunches()

  useEffect(() => {
    fetchBunches()
  }, [fetchBunches])

  const params = useParams()
  const [isOpen, setIsOpen] = useState(false)

  const currentBunchId = params?.bunchId as string

  // Get the current bunch if there's an ID in the params
  const currentBunch = bunches?.find(bunch => bunch.id === currentBunchId)

  const toggleSidebar = () => {
    setIsOpen(!isOpen)
  }

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
          "bg-card border-border fixed inset-y-0 left-0 z-30 flex flex-col border transition-transform duration-300 ease-in-out",
          "m-2 w-15 rounded-lg",
          isOpen ? "translate-x-0" : "-translate-x-full",
          "md:relative md:translate-x-0 md:items-center",
          "flex h-[calc(100vh-1rem)] flex-col", // Ensure it takes full height minus margin
        )}
      >
        <div className="grow overflow-hidden">
          <div className="scrollbar-hide flex h-full flex-col items-center overflow-y-auto p-2">
            <div className="flex grow flex-col items-center space-y-2">
              {bunches.map(bunch => (
                <TooltipProvider key={bunch.id}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Link
                        href={`/bunch/${bunch.id}`}
                        className="flex h-12 w-12 items-center justify-center rounded-[100px] bg-(--bunch-primary-color)/20 transition-all hover:rounded-[15px]"
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
                                "bg-transparent text-lg text-(--bunch-primary-color)",
                                currentBunchId === bunch.id && "text-primary",
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

            <div className="mt-4 flex flex-col items-center gap-2">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <CreateBunchButton>
                      <div className="flex h-12 w-12 items-center justify-center rounded-full">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="bg-primary/10 hover:bg-primary/20! h-full w-full rounded-[100px] p-0 opacity-60 transition-all hover:rounded-[15px]"
                        >
                          <Plus className="h-6! w-6!" />
                          <span className="sr-only">Create Bunch</span>
                        </Button>
                      </div>
                    </CreateBunchButton>
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
                      className="flex h-12 w-12 items-center justify-center rounded-full"
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        className="bg-primary/10 hover:bg-primary/20! h-full w-full rounded-[100px] p-0 opacity-60 transition-all hover:rounded-[15px]"
                      >
                        <Globe2Icon className="h-5! w-5!" />
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
                    <div className="flex h-12 w-12 items-center justify-center">
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
                      className="flex h-12 w-12 items-center justify-center rounded-full"
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        className="bg-primary/10 hover:bg-primary/20! h-full w-full rounded-[100px] p-0 opacity-60 transition-all hover:rounded-[15px]"
                      >
                        <MessageCircle className="h-5! w-5!" />
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
                      className="flex h-12 w-12 items-center justify-center rounded-full"
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        className="bg-primary/10 hover:bg-primary/20! h-full w-full rounded-[100px] p-0 opacity-60 transition-all hover:rounded-[15px]"
                      >
                        <Settings className="h-5! w-5!" />
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
                    <div className="bg-primary/5 hover:bg-primary/60 flex h-12 w-12 items-center justify-center rounded-full transition-colors">
                      <UserButton />
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
    </>
  )
}
