"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import { Hash, Mic, Phone, Plus, Search, Settings, Video, Volume2, Gamepad2, Headphones } from "lucide-react"

export default function HeroInterface() {
    return (
        <div
            style={{
                pointerEvents: "none",
                userSelect: "none",
                // @ts-ignore
                "--Sidebar-width": "260px",
                width: "100%",
                height: "900px"
            }}
        >
            <div
                style={{
                    perspective: "4000px",
                    perspectiveOrigin: "100% 0",
                    width: "100%",
                    height: "100%",
                    transformStyle: "preserve-3d",
                    position: "relative"
                }}
            >
                <div
                    className="absolute overflow-hidden bg-gray-950 shadow-2xl"
                    style={{
                        background: "#030712", // var(--color-bg-primary)
                        transformOrigin: "0 0",
                        backfaceVisibility: "hidden",
                        border: "1px solid #1e1e1e",
                        borderRadius: "10px",
                        width: "1600px",
                        height: "900px",
                        margin: "100px auto auto",
                        position: "absolute",
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0,
                        transform: "translate(-10%) scale(1.2) rotateX(47deg) rotateY(31deg) rotate(324deg)",
                        boxShadow: "0 0 0 1px rgba(255,255,255,0.05), -20px 40px 100px -12px rgba(0, 0, 0, 0.8)",
                        WebkitFontSmoothing: "antialiased",
                        maskImage: "linear-gradient(to bottom, black 75%, transparent 100%), linear-gradient(to right, black 85%, transparent 98%)",
                        maskComposite: "intersect",
                        WebkitMaskImage: "linear-gradient(to bottom, black 85%, transparent 100%), linear-gradient(to right, black 85%, transparent 98%)",
                        WebkitMaskComposite: "source-in"
                    }}
                >
                    {/* Content */}
                    <div className="flex h-full bg-background/95">
                        {/* Sidebar (Server List) */}
                        <div className="w-[72px] bg-muted/30 flex flex-col items-center py-4 gap-3 border-r hidden sm:flex">
                            <div className="w-12 h-12 rounded-[16px] bg-primary flex items-center justify-center text-primary-foreground transition-all hover:rounded-[12px] cursor-pointer shadow-lg shadow-primary/20">
                                <Gamepad2 className="w-7 h-7" />
                            </div>
                            <Separator className="w-8 bg-border/50" />
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="group relative w-12 h-12 flex items-center justify-center cursor-pointer">
                                    <div className="absolute left-0 w-1 h-2 bg-foreground rounded-r-full -ml-4 opacity-0 group-hover:opacity-100 group-hover:h-5 transition-all" />
                                    <div className="w-12 h-12 rounded-[24px] bg-muted group-hover:bg-primary/20 group-hover:rounded-[16px] transition-all flex items-center justify-center text-muted-foreground group-hover:text-primary overflow-hidden">
                                        <span className="font-bold">S{i}</span>
                                    </div>
                                </div>
                            ))}
                            <div className="w-12 h-12 rounded-[24px] bg-muted hover:bg-green-500/20 text-muted-foreground hover:text-green-500 transition-all flex items-center justify-center cursor-pointer border border-dashed border-muted-foreground/30">
                                <Plus className="w-6 h-6" />
                            </div>
                        </div>

                        {/* Secondary Sidebar (Channels) */}
                        <div className="w-60 bg-muted/10 flex flex-col border-r hidden md:flex">
                            <div className="h-12 border-b flex items-center px-4 font-bold shadow-sm">
                                Product Design <span className="ml-auto text-xs text-muted-foreground">v2.0</span>
                            </div>
                            <ScrollArea className="flex-1 p-3">
                                <div className="mb-6">
                                    <div className="flex items-center justify-between px-2 text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 group">
                                        <span>Information</span>
                                        <Plus className="w-3 h-3 opacity-0 group-hover:opacity-100 cursor-pointer" />
                                    </div>
                                    <div className="space-y-0.5">
                                        <ChannelItem active icon={Hash} name="general" />
                                        <ChannelItem icon={Hash} name="announcements" />
                                        <ChannelItem icon={Hash} name="resources" />
                                    </div>
                                </div>
                                <div className="mb-6">
                                    <div className="flex items-center justify-between px-2 text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 group">
                                        <span>Voice Channels</span>
                                        <Plus className="w-3 h-3 opacity-0 group-hover:opacity-100 cursor-pointer" />
                                    </div>
                                    <div className="space-y-0.5">
                                        <ChannelItem icon={Volume2} name="Lobby" type="voice" />
                                        <ChannelItem icon={Volume2} name="Gaming" type="voice" />
                                    </div>
                                </div>
                            </ScrollArea>
                            <div className="h-14 bg-muted/20 flex items-center px-2 gap-2 border-t">
                                <Avatar className="w-8 h-8">
                                    <AvatarImage src="/avatar-placeholder.png" />
                                    <AvatarFallback className="bg-primary/20 text-primary text-xs">ME</AvatarFallback>
                                </Avatar>
                                <div className="flex-1 min-w-0">
                                    <div className="text-sm font-bold truncate">Current User</div>
                                    <div className="text-xs text-muted-foreground truncate">#1234</div>
                                </div>
                                <div className="flex gap-1">
                                    <Mic className="w-4 h-4 text-muted-foreground hover:text-foreground cursor-pointer" />
                                    <Headphones className="w-4 h-4 text-muted-foreground hover:text-foreground cursor-pointer" />
                                    <Settings className="w-4 h-4 text-muted-foreground hover:text-foreground cursor-pointer" />
                                </div>
                            </div>
                        </div>

                        {/* Main Content (Chat) */}
                        <div className="flex-1 flex flex-col bg-background relative">
                            <div className="h-12 border-b flex items-center px-4 justify-between shrink-0 shadow-sm z-10">
                                <div className="flex items-center gap-2">
                                    <Hash className="w-5 h-5 text-muted-foreground" />
                                    <span className="font-bold">general</span>
                                    <div className="w-px h-4 bg-border/50 mx-2" />
                                    <span className="text-xs text-muted-foreground truncate max-w-[200px]">General discussion about the new features</span>
                                </div>
                                <div className="flex items-center gap-4 text-muted-foreground">
                                    <Phone className="w-5 h-5 hover:text-foreground cursor-pointer" />
                                    <Video className="w-5 h-5 hover:text-foreground cursor-pointer" />
                                    <div className="w-64 bg-muted/40 h-7 rounded text-xs flex items-center px-2">
                                        Search
                                    </div>
                                </div>
                            </div>

                            <ScrollArea className="flex-1 p-4">
                                <div className="flex flex-col justify-end min-h-full space-y-6 pb-4">
                                    <div className="flex items-center gap-4 px-4 py-6">
                                        <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                                            <Hash className="w-8 h-8 text-primary" />
                                        </div>
                                        <div>
                                            <h1 className="text-3xl font-bold">Welcome to #general!</h1>
                                            <p className="text-muted-foreground">This is the start of the <span className="font-medium text-foreground">#general</span> channel.</p>
                                        </div>
                                    </div>

                                    <Separator className="my-2" />

                                    <Message
                                        username="Sarah Chen"
                                        color="text-red-400"
                                        time="Today at 9:42 AM"
                                        content="Has anyone checked the latest designs for the dashboard? They look amazing! 🎨"
                                    />
                                    <Message
                                        username="Alex Rivera"
                                        color="text-primary"
                                        time="Today at 9:43 AM"
                                        content="Yeah, I just saw them. The new dark mode implementation is spot on."
                                        isReply
                                    />
                                    <Message
                                        username="David Kim"
                                        color="text-blue-400"
                                        time="Today at 9:45 AM"
                                        content="I'm working on the component library updates. Should be ready by EOD."
                                    />
                                    <Message
                                        username="Justine Mod"
                                        color="text-yellow-400"
                                        time="Today at 10:00 AM"
                                        content="Great work team! Let's sync up later to discuss the rollout plan."
                                        badge="Admin"
                                    />
                                    <Message
                                        username="Sarah Chen"
                                        color="text-red-400"
                                        time="Today at 10:05 AM"
                                        content="Just pushed the initial commit for the hero section."
                                    />
                                </div>
                            </ScrollArea>

                            <div className="p-4 pt-0 shrink-0">
                                <div className="bg-muted/30 rounded-lg p-3 flex items-center gap-3 border shadow-inner">
                                    <div className="w-6 h-6 rounded-full bg-muted-foreground/30 flex items-center justify-center cursor-pointer hover:bg-muted-foreground/50 transition-colors">
                                        <Plus className="w-4 h-4 text-background" />
                                    </div>
                                    <input
                                        className="bg-transparent border-none outline-none flex-1 text-sm placeholder:text-muted-foreground/70"
                                        placeholder="Message #general"
                                        readOnly
                                    />
                                    <div className="flex gap-2 text-muted-foreground">
                                        <Gamepad2 className="w-5 h-5 hover:text-foreground cursor-pointer" />
                                        <Mic className="w-5 h-5 hover:text-foreground cursor-pointer" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* User List (Right Sidebar) */}
                        <div className="w-60 bg-muted/10 border-l hidden lg:flex flex-col p-3">
                            <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">Online — 4</div>
                            <div className="space-y-1">
                                <UserItem name="Justine Mod" color="text-yellow-400" status="online" badge="Admin" />
                                <UserItem name="Alex Rivera" color="text-primary" status="dnd" />
                                <UserItem name="Sarah Chen" color="text-red-400" status="idle" />
                                <UserItem name="David Kim" color="text-blue-400" status="online" />
                            </div>
                        </div>

                    </div>
                </div>

                {/* <div className="fixed bottom-4 right-4 p-4 bg-background/90 backdrop-blur border rounded-lg shadow-xl z-50 w-80 space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm">3D Controls</h3>
                    <button
                        onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify(transform, null, 2))
                            alert("Copied config to clipboard!")
                        }}
                        className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded"
                    >
                        Copy Config
                    </button>
                </div>

                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <label>Perspective</label>
                        <span>{transform.perspective}px</span>
                    </div>
                    <input
                        type="range" min="500" max="5000" step="100"
                        value={transform.perspective}
                        onChange={(e) => setTransform(p => ({ ...p, perspective: Number(e.target.value) }))}
                        className="w-full"
                    />
                </div>

                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <label>Rotate X</label>
                        <span>{transform.rotateX}°</span>
                    </div>
                    <input
                        type="range" min="0" max="60" step="1"
                        value={transform.rotateX}
                        onChange={(e) => setTransform(p => ({ ...p, rotateX: Number(e.target.value) }))}
                        className="w-full"
                    />
                </div>

                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <label>Rotate Y</label>
                        <span>{transform.rotateY}°</span>
                    </div>
                    <input
                        type="range" min="-45" max="45" step="1"
                        value={transform.rotateY}
                        onChange={(e) => setTransform(p => ({ ...p, rotateY: Number(e.target.value) }))}
                        className="w-full"
                    />
                </div>

                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <label>Rotate Z</label>
                        <span>{transform.rotateZ}°</span>
                    </div>
                    <input
                        type="range" min="-20" max="20" step="1"
                        value={transform.rotateZ}
                        onChange={(e) => setTransform(p => ({ ...p, rotateZ: Number(e.target.value) }))}
                        className="w-full"
                    />
                </div>

                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <label>Scale</label>
                        <span>{transform.scale}</span>
                    </div>
                    <input
                        type="range" min="0.5" max="1.5" step="0.05"
                        value={transform.scale}
                        onChange={(e) => setTransform(p => ({ ...p, scale: Number(e.target.value) }))}
                        className="w-full"
                    />
                </div>
            </div> */}
            </div>
        </div>
    )
}

function ChannelItem({ icon: Icon, name, active, type = 'text' }: { icon: any, name: string, active?: boolean, type?: 'text' | 'voice' }) {
    return (
        <div className={cn(
            "flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer group transition-colors",
            active ? "bg-muted-foreground/10 text-foreground" : "text-muted-foreground hover:bg-muted-foreground/5 hover:text-foreground"
        )}>
            <Icon className="w-4 h-4 text-muted-foreground/70" />
            <span className={cn("text-sm font-medium", active && "font-semibold")}>{name}</span>
            {type === 'voice' && (
                <div className="ml-auto w-10 flex -space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-5 h-5 rounded-full border-2 border-background bg-muted" />
                    <div className="w-5 h-5 rounded-full border-2 border-background bg-muted" />
                </div>
            )}
        </div>
    )
}

function Message({ username, time, content, color, isReply, badge }: { username: string, time: string, content: string, color?: string, isReply?: boolean, badge?: string }) {
    return (
        <div className={cn("group flex items-start gap-4 px-2 py-1 -mx-2 rounded hover:bg-muted/30 transition-colors", isReply && "mt-1")}>
            <div className="mt-0.5">
                <Avatar className="w-10 h-10 transition-transform active:scale-95 cursor-pointer">
                    <AvatarFallback className={cn("text-white text-xs font-bold", color ? color.replace('text-', 'bg-') : 'bg-muted-foreground')}>
                        {username.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                </Avatar>
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                    <span className={cn("font-semibold text-sm cursor-pointer hover:underline", color)}>{username}</span>
                    {badge && <span className="bg-primary/20 text-primary text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wide">{badge}</span>}
                    <span className="text-[10px] text-muted-foreground/70">{time}</span>
                </div>
                <p className="text-[15px] leading-relaxed text-foreground/90">{content}</p>
            </div>
        </div>
    )
}

function UserItem({ name, status, color, badge }: { name: string, status: 'online' | 'idle' | 'dnd' | 'offline', color?: string, badge?: string }) {
    const statusColor = {
        online: "bg-green-500",
        idle: "bg-orange-500",
        dnd: "bg-red-500",
        offline: "bg-muted-foreground"
    }[status]

    return (
        <div className="flex items-center gap-3 px-2 py-1.5 rounded-md hover:bg-muted/30 cursor-pointer opacity-90 hover:opacity-100 transition-all">
            <div className="relative">
                <Avatar className="w-8 h-8">
                    <AvatarFallback className={cn("text-white text-[10px] font-bold", color ? color.replace('text-', 'bg-') : 'bg-muted-foreground')}>
                        {name.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                </Avatar>
                <div className={cn("absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-[3px] border-black/10 dark:border-[#1e1e1e]", statusColor)} />
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                    <span className={cn("text-sm font-medium truncate", color)}>{name}</span>
                    {badge && <span className="bg-primary/20 text-primary text-[10px] w-4 h-4 flex items-center justify-center rounded font-bold">✓</span>}
                </div>
                <div className="text-xs text-muted-foreground truncate opacity-70">Playing VS Code</div>
            </div>
        </div>
    )
}
