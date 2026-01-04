"use client"

import { cn } from "@/lib/utils"
import { Lock, Check, FileText, Puzzle, Bot, Zap, Globe, Github } from "lucide-react"

export const IntegrationsVisual = () => {
    return (
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative w-full h-full p-8 flex items-center justify-center">
                {/* Central Node */}
                <div className="absolute z-10 w-16 h-16 bg-primary rounded-2xl flex items-center justify-center shadow-xl shadow-primary/20 animate-pulse">
                    <Bot className="w-8 h-8 text-primary-foreground" />
                </div>

                {/* Orbiting Nodes */}
                <div className="absolute w-[200px] h-[200px] border border-dashed border-primary/20 rounded-full animate-[spin_20s_linear_infinite]" />
                <div className="absolute w-[140px] h-[140px] border border-dashed border-primary/20 rounded-full animate-[spin_15s_linear_infinite_reverse]" />

                {/* Floating Icons */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] animate-[spin_20s_linear_infinite]">
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-8 h-8 bg-background border rounded-lg flex items-center justify-center shadow-sm">
                        <Github className="w-5 h-5" />
                    </div>
                    <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-8 h-8 bg-background border rounded-lg flex items-center justify-center shadow-sm">
                        <Globe className="w-5 h-5 text-blue-500" />
                    </div>
                </div>

                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140px] h-[140px] animate-[spin_15s_linear_infinite_reverse]">
                    <div className="absolute top-1/2 -right-3 -translate-y-1/2 w-8 h-8 bg-background border rounded-lg flex items-center justify-center shadow-sm">
                        <Zap className="w-5 h-5 text-yellow-500" />
                    </div>
                    <div className="absolute top-1/2 -left-3 -translate-y-1/2 w-8 h-8 bg-background border rounded-lg flex items-center justify-center shadow-sm">
                        <Puzzle className="w-5 h-5 text-purple-500" />
                    </div>
                </div>
            </div>
        </div>
    )
}

export const FilesVisual = () => {
    return (
        <div className="absolute inset-0 flex items-center justify-center p-6">
            <div className="relative w-full max-w-[200px] h-32 bg-background border rounded-lg shadow-sm rotate-[-5deg] hover:rotate-0 transition-transform duration-300 z-10 flex flex-col items-center justify-center p-4 gap-2">
                <FileText className="w-8 h-8 text-blue-500" />
                <div className="h-2 w-16 bg-muted rounded" />
                <div className="h-2 w-12 bg-muted/50 rounded" />
            </div>
            <div className="absolute w-full max-w-[200px] h-32 bg-background/50 border rounded-lg shadow-sm rotate-[5deg] translate-x-4 translate-y-2 flex flex-col items-center justify-center p-4 gap-2">
                <FileText className="w-8 h-8 text-orange-500" />
                <div className="h-2 w-16 bg-muted rounded" />
                <div className="h-2 w-12 bg-muted/50 rounded" />
            </div>
        </div>
    )
}

export const SpeedVisual = () => {
    return (
        <div className="absolute right-0 top-10 h-full w-[80%] [mask-image:linear-gradient(to_bottom,white,transparent)]">
            <div className="flex flex-col gap-2 p-4">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center gap-2 rounded-lg bg-background/50 p-3 shadow border animate-in slide-in-from-right fade-in duration-500" style={{ animationDelay: `${i * 150}ms` }}>
                        <div className="h-8 w-8 shrink-0 rounded-full bg-primary/20" />
                        <div className="space-y-1">
                            <div className="h-2 w-20 rounded bg-muted-foreground/20" />
                            <div className="h-2 w-32 rounded bg-muted-foreground/20" />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export const SecurityVisual = () => {
    return (
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative h-32 w-32 rounded-full border-2 border-dashed border-primary/20 animate-[spin_10s_linear_infinite]">
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-16 w-16 bg-primary/10 rounded-xl flex items-center justify-center backdrop-blur-md border shadow-lg">
                    <Lock className="h-8 w-8 text-primary animate-pulse" />
                </div>
            </div>
        </div>
    )
}

export const UniversalVisual = () => {
    return (
        <div className="absolute bottom-0 right-0 h-[80%] w-[90%] md:w-[70%]">
            <div className="relative h-full w-full rounded-tl-xl border-l border-t bg-background shadow-2xl overflow-hidden p-4">
                <div className="flex gap-2 mb-4">
                    <div className="h-3 w-3 rounded-full bg-red-500/50" />
                    <div className="h-3 w-3 rounded-full bg-yellow-500/50" />
                    <div className="h-3 w-3 rounded-full bg-green-500/50" />
                </div>
                <div className="space-y-2">
                    <div className="h-4 w-1/3 bg-muted rounded"></div>
                    <div className="h-24 w-full bg-muted/30 rounded border-dashed border-2"></div>
                </div>

                {/* Phone Mockup overlay */}
                <div className="absolute bottom-0 right-4 h-48 w-24 bg-background border-l border-t border-r rounded-t-xl shadow-xl p-2">
                    <div className="h-1 w-8 bg-muted mx-auto rounded mb-2"></div>
                    <div className="space-y-1">
                        <div className="h-8 w-full bg-primary/10 rounded"></div>
                        <div className="h-8 w-full bg-muted/30 rounded"></div>
                        <div className="h-8 w-full bg-muted/30 rounded"></div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export const ThreadsVisual = () => {
    return (
        <div className="absolute right-4 top-8 w-[200px] space-y-2">
            <div className="rounded-lg bg-background p-3 shadow-sm border">
                <div className="h-2 w-12 bg-primary/20 rounded mb-2"></div>
                <div className="h-2 w-full bg-muted rounded"></div>
            </div>

            <div className="relative pl-6 space-y-2">
                {/* Thread Line */}
                <div className="absolute left-3 top-[-10px] bottom-4 w-0.5 bg-border rounded-bl-lg"></div>
                <div className="absolute left-3 top-[18px] w-3 h-0.5 bg-border"></div>

                <div className="rounded-lg bg-muted/20 p-2 text-xs">
                    <div className="h-2 w-8 bg-muted-foreground/20 rounded mb-1"></div>
                    <div className="h-1.5 w-3/4 bg-muted-foreground/10 rounded"></div>
                </div>

                <div className="rounded-lg bg-muted/20 p-2 text-xs relative">
                    <div className="absolute left-[-12px] top-[14px] w-3 h-0.5 bg-border"></div>
                    <div className="h-2 w-8 bg-muted-foreground/20 rounded mb-1"></div>
                    <div className="h-1.5 w-2/3 bg-muted-foreground/10 rounded"></div>
                </div>
            </div>
        </div>
    )
}

export const RolesVisual = () => {
    return (
        <div className="absolute inset-0 flex items-center justify-center p-6">
            <div className="grid grid-cols-2 gap-4 w-full max-w-sm">
                <div className="aspect-square rounded-xl bg-background border p-4 flex flex-col items-center justify-center gap-2 shadow-sm hover:scale-105 transition-transform duration-300">
                    <div className="h-10 w-10 rounded-full bg-red-500/20" />
                    <div className="h-2 w-16 bg-muted rounded" />
                    <div className="px-2 py-0.5 rounded-full bg-red-500/10 text-[10px] text-red-500 font-bold uppercase">Admin</div>
                </div>
                <div className="aspect-square rounded-xl bg-background border p-4 flex flex-col items-center justify-center gap-2 shadow-sm mt-8 hover:scale-105 transition-transform duration-300">
                    <div className="h-10 w-10 rounded-full bg-blue-500/20" />
                    <div className="h-2 w-16 bg-muted rounded" />
                    <div className="px-2 py-0.5 rounded-full bg-blue-500/10 text-[10px] text-blue-500 font-bold uppercase">Member</div>
                </div>
            </div>
        </div>
    )
}

export const KeyboardVisual = () => {
    return (
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-[80%] rounded-xl bg-background border shadow-2xl p-2">
                <div className="flex items-center gap-2 border-b pb-2 px-2">
                    <div className="h-4 w-4 text-muted-foreground" >⌘</div>
                    <div className="text-sm text-muted-foreground">Type a command...</div>
                </div>
                <div className="pt-2 space-y-1">
                    <div className="flex items-center justify-between p-2 rounded bg-primary/10 text-primary text-sm font-medium">
                        <span>Find Channel...</span>
                        <span className="text-xs opacity-70">↵</span>
                    </div>
                    <div className="flex items-center justify-between p-2 rounded hover:bg-muted text-muted-foreground text-sm">
                        <span>Create Bunch</span>
                        <span className="text-xs opacity-50">^C</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
