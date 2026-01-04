"use client"

import React, { useMemo } from 'react'
import { cn } from "@/lib/utils"

interface InteractiveGridProps {
    cols?: number
    rows?: number
    className?: string
}

export const InteractiveGrid = ({
    cols = 20,
    rows = 10,
    className
}: InteractiveGridProps) => {
    const items = useMemo(() => {
        return Array.from({ length: cols * rows }).map((_, i) => ({
            id: i,
            grade: Math.floor(Math.random() * 12 - 6),
            opacity: Math.min(Math.random(), 0.2),
            hue: Math.floor(Math.random() * 30)
        }));
    }, [cols, rows]);

    return (
        <div
            className={cn("grid w-full h-full", className)}
            style={{
                gridTemplateColumns: `repeat(${cols}, 1fr)`,
                gridTemplateRows: `repeat(${rows}, 1fr)`,
                touchAction: 'none',
            } as React.CSSProperties}
        >
            {items.map((item) => (
                <div
                    key={item.id}
                    className="group/item relative flex items-center justify-center p-0.5 aspect-square scale-150 transition-[opacity,rotate,filter] duration-800 ease-in [transition-duration:0.8s,0.4s,0.6s] [transition-timing-function:ease-in,ease-out,ease-out] grayscale opacity-100 hover:duration-0 hover:grayscale-0 hover:brightness-150 hover:opacity-100 hover:rotate-[calc(var(--item-grade)*90deg)] hover:z-10"
                    style={{
                        '--item-grade': item.grade,
                        '--item-opacity': item.opacity,
                        color: '#00000045',
                    } as React.CSSProperties}
                >
                    <span className="text-2xl font-mono font-bold select-none">#</span>
                </div>
            ))}
        </div>
    )
}
