"use client"

import { Button } from "@/components/ui/button"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <ThemeToggleButton theme={theme} setTheme={setTheme} />
  }

  return (
    <ThemeToggleButton
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      theme={theme}
      setTheme={setTheme}
    />
  )
}

function ThemeToggleButton({
  title,
  theme,
  setTheme,
}: {
  title?: string
  theme?: string
  setTheme: (theme: string) => void
}) {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      title={title || "Toggle Theme"}
      className="bg-primary/10 hover:bg-primary/20! relative h-full w-full rounded-[100px] p-0 opacity-60 transition-all hover:rounded-[15px]"
    >
      <Sun className="h-5! w-5! scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <Moon className="absolute inset-0 m-auto h-5! w-5! scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
    </Button>
  )
}
