"use client"

import Link from "next/link"
import { Command } from "@phosphor-icons/react"
import { NavigationMenuDemo } from "@/components/landing/NavigationMenuDemo"
import { ThemeToggle } from "@/components/theme/ThemeToggle"
import { SignOutButton } from "@/components/auth/SignOutButton"
import { Button } from "@/components/ui/button"

interface NavbarProps {
    user: any
}

export function Navbar({ user }: NavbarProps) {
    return (
        <div className="fixed top-6 left-0 right-0 z-50 flex justify-center px-6 pointer-events-none">
            <header className="pointer-events-auto flex h-14 items-center justify-between gap-4 rounded-full border bg-background/80 px-2 pl-4 backdrop-blur-md shadow-md w-full max-w-5xl">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2 font-bold text-lg hover:opacity-90 transition-opacity">
                    <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground">
                        <Command className="w-4 h-4" />
                    </div>
                    <span>Bunch</span>
                </Link>

                {/* Navigation - Centered */}
                <div className="hidden md:flex flex-1 justify-center">
                    <NavigationMenuDemo />
                </div>

                {/* Right Side Actions */}
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8">
                        <ThemeToggle />
                    </div>

                    {user ? (
                        <SignOutButton />
                    ) : (
                        <div className="hidden sm:flex gap-2">
                            <Button variant="ghost" size="sm" className="rounded-full h-9 px-4" asChild>
                                <Link href="/auth/sign-in">Log in</Link>
                            </Button>
                            <Button size="sm" className="rounded-full h-9 px-4" asChild>
                                <Link href="/auth/sign-up">Sign up</Link>
                            </Button>
                        </div>
                    )}
                </div>
            </header>
        </div>
    )
}
