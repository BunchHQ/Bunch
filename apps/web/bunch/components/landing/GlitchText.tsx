"use client"

import React, { useState, useEffect, useRef } from "react"
import { cn } from "@/lib/utils"

interface GlitchTextProps {
    text: string
    hoverText: string
    className?: string
}

const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+"

export function GlitchText({ text, hoverText, className }: GlitchTextProps) {
    const [displayText, setDisplayText] = useState(text)
    const intervalRef = useRef<NodeJS.Timeout | null>(null)
    const isHovering = useRef(false)

    const scramble = (targetText: string) => {
        let iteration = 0

        if (intervalRef.current) clearInterval(intervalRef.current)

        intervalRef.current = setInterval(() => {
            setDisplayText((prev) =>
                targetText
                    .split("")
                    .map((char, index) => {
                        if (index < iteration) {
                            return targetText[index]
                        }
                        return CHARS[Math.floor(Math.random() * CHARS.length)]
                    })
                    .join("")
            )

            if (iteration >= targetText.length) {
                if (intervalRef.current) clearInterval(intervalRef.current)
            }

            iteration += 1 / 3
        }, 30)
    }

    const handleMouseEnter = () => {
        isHovering.current = true
        scramble(hoverText)
    }

    const handleMouseLeave = () => {
        isHovering.current = false
        scramble(text)
    }

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current)
        }
    }, [])

    return (
        <span
            className={cn("inline-block cursor-pointer", className)}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {displayText}
        </span>
    )
}
