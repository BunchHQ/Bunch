"use client"

import Link from "next/link"
import { GithubLogo, Star, StarIcon } from "@phosphor-icons/react"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"

export function GithubButton() {
    const [stars, setStars] = useState<number | null>(null)

    useEffect(() => {
        fetch("https://api.github.com/repos/bunchhq/bunch")
            .then((res) => res.json())
            .then((data) => setStars(data.stargazers_count))
            .catch(() => setStars(null))
    }, [])

    return (
        <Button variant="ghost" size="sm" className="rounded-full h-8 px-3 gap-2 text-muted-foreground hover:text-foreground" asChild>
            <Link href="https://github.com/bunchhq/bunch" target="_blank" rel="noopener noreferrer">
                {/* <StarIcon className="w-4 h-4" /> */}
                <span className="font-medium">Star</span>
                {stars !== null && (
                    <div className="flex items-center gap-1 pl-1 border-l ml-1 border-muted-foreground/30">
                        <span className="text-xs">{stars}</span>
                    </div>
                )}
            </Link>
        </Button>
    )
}
