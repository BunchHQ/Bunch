"use client"

import { useMembers } from "@/lib/hooks"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { useEffect } from "react"

interface MembersPanelProps {
    bunchId: string
    className?: string
}

export function MembersPanel({ bunchId, className }: MembersPanelProps) {
    const { members, loading, error, fetchMembers } = useMembers(bunchId)

    useEffect(() => {
        fetchMembers()
    }, [fetchMembers])

    if (loading) {
        return (
            <div className={cn("w-60 border-l p-4", className)}>
                <h3 className="mb-4 font-semibold">Members</h3>
                <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="flex items-center gap-2">
                            <div className="h-8 w-8 animate-pulse rounded-full bg-secondary" />
                            <div className="h-4 w-24 animate-pulse rounded bg-secondary" />
                        </div>
                    ))}
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className={cn("w-60 border-l p-4 text-sm text-destructive", className)}>
                Failed to load members
            </div>
        )
    }

    return (
        <div className={cn("hidden w-60 flex-col border-l border-border bg-background sm:flex", className)}>
            <div className="p-4 shadow-sm">
                <h3 className="font-semibold">Members — {members.length}</h3>
            </div>
            <ScrollArea className="flex-1 px-4 pb-4">
                <div className="space-y-4">
                    {members.map((member) => (
                        <div key={member.id} className="flex items-center gap-2">
                            <div className="relative">
                                <Avatar className="h-8 w-8">
                                    <AvatarImage src={member.user.avatar} alt={member.user.username} />
                                    <AvatarFallback>{member.user.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                                </Avatar>
                                {/* Status indicator could go here */}
                                {member.user.status === "online" && (
                                    <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full bg-green-500 ring-2 ring-background" />
                                )}
                            </div>
                            <div className="overflow-hidden">
                                <p className="truncate text-sm font-medium leading-none">
                                    {member.user.display_name || member.user.username}
                                </p>
                                {member.user.display_name && (
                                    <p className="truncate text-xs text-muted-foreground">
                                        {member.user.username}
                                    </p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </ScrollArea>
        </div>
    )
}
