"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { createClient } from "@/lib/supabase/client"
import { User as SupabaseUser } from "@supabase/supabase-js"
import { Loader2Icon, LogInIcon, LogOutIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

export function UserButton() {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const router = useRouter()

  const supabase = createClient()

  useEffect(() => {
    const getUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }

    getUser()
  }, [])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setOpen(false)
    router.push("/")
  }

  if (loading) {
    return (
      <button disabled>
        <Loader2Icon className="size-4 animate-spin" />
      </button>
    )
  }

  if (!user) {
    return (
      <button onClick={() => router.push("/auth/login")}>
        <LogInIcon className="size-4" />
      </button>
    )
  }

  const displayName: string | undefined = user.user_metadata.display_name
  const username: string | undefined = user.user_metadata.username
  const email = user.email

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-12 w-12 rounded-md p-0">
          <Avatar className="h-12 w-12">
            <AvatarFallback className="bg-primary/10 text-sm">
              {displayName?.charAt(0) || username?.charAt(0) || email?.charAt(0)}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-auto max-w-96 min-w-64">
        <div className="space-y-3 px-4 py-3">
          <div>
            {displayName ? (
              <p className="text-foreground text-sm">{displayName}</p>
            ) : (
              <p className="text-muted-foreground text-sm italic">No Display Name</p>
            )}
            {username ? (
              <p className="text-muted-foreground text-xs font-semibold">@{username}</p>
            ) : (
              <p className="text-muted-foreground text-xs italic">No Username</p>
            )}
          </div>
          <p className="text-muted-foreground text-xs font-medium break-all">{email}</p>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleSignOut} className="cursor-pointer">
          <LogOutIcon className="mr-2 size-4" />
          <span>Sign Out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
