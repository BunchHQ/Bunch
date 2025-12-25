"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useCurrentUser } from "@/lib/hooks"
import { useRouter } from "next/navigation"
import { useEffect, useMemo, useState } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

const colors = [
  { name: "Ruby", value: "ruby", hex: "#c02c38" },
  { name: "Emerald", value: "emerald", hex: "#2ecc71" },
  { name: "Sapphire", value: "sapphire", hex: "#3498db" },
  { name: "Amber", value: "amber", hex: "#e6b32e" },
  { name: "Violet", value: "violet", hex: "#9b59b6" },
  { name: "Coral", value: "coral", hex: "#e67e22" },
  { name: "Rose", value: "rose", hex: "#e84393" },
  { name: "Slate", value: "slate", hex: "#34495e" },
  { name: "Ivory", value: "ivory", hex: "#f5f5f0" },
  { name: "Silver", value: "silver", hex: "#bdc3c7" },
  { name: "Teal", value: "teal", hex: "#16a085" },
  { name: "Crimson", value: "crimson", hex: "#e74c3c" },
  { name: "Lavender", value: "lavender", hex: "#967bb6" },
  { name: "Mint", value: "mint", hex: "#00b894" },
  { name: "Indigo", value: "indigo", hex: "#5352ed" },
  { name: "Honey", value: "honey", hex: "#fbc531" },
]

function getRandomColor() {
  return colors[Math.floor(Math.random() * colors.length)].hex
}

const formSchema = z.object({
  status: z.string().optional(),
  bio: z.string().optional(),
  pronoun: z.string().optional(),
  theme: z.enum(["system", "light", "dark"]).default("system"),
  color: z.enum(colors.map(c => c.hex)).default(getRandomColor()),
})

type FormData = z.infer<typeof formSchema>

export default function OnboardingPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const { onboardUser } = useCurrentUser()

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      status: "",
      bio: "",
      pronoun: "",
      theme: "system",
    },
  })

  useEffect(() => {
    setMounted(true)
    setValue("color", getRandomColor())
  }, [setValue])

  const color = watch("color")
  const selectedColor = useMemo(() => colors.find(c => c.hex === color), [color])

  const onSubmit = async (data: any) => {
    setIsLoading(true)
    console.log(data)
    try {
      const onboardingData = await onboardUser(data)
      console.log(onboardingData)
      toast("Success", {
        description: "Onboarding completed successfully!",
      })

      reset()

      // to the app
      router.push(`/app`)
    } catch (error) {
      toast("Error", {
        description: error instanceof Error ? error.message : "Failed to complete onboarding",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-lg">
        <div className="relative h-16 overflow-hidden rounded-t-lg">
          <div className="absolute inset-0 opacity-45">
            <div className="absolute top-2 left-4 text-3xl">✨</div>
            <div className="absolute right-4 bottom-2 text-2xl">🎨</div>
            <div className="absolute top-1/2 left-1/3 text-2xl">🚀</div>
          </div>
        </div>
        <CardHeader className="pb-4">
          <CardTitle className="text-2xl">Welcome aboard! 🎉</CardTitle>
          <CardDescription>Let's make your profile uniquely you</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="status" className="font-medium">
                Set a status? 💭
              </Label>
              <Input
                id="status"
                placeholder="What's on your mind?"
                {...register("status")}
                disabled={isLoading}
              />
              {errors.status && <p className="text-destructive text-sm">{errors.status.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio" className="font-medium">
                Tell us about yourself 👋
              </Label>
              <Textarea
                id="bio"
                placeholder="Share a bit about yourself..."
                {...register("bio")}
                rows={4}
                disabled={isLoading}
              />
              {errors.bio && <p className="text-destructive text-sm">{errors.bio.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="pronoun" className="font-medium">
                Your pronouns
              </Label>
              <Input
                id="pronoun"
                placeholder="Enter your pronouns..."
                {...register("pronoun")}
                disabled={isLoading}
              />
              {errors.pronoun && (
                <p className="text-destructive text-sm">{errors.pronoun.message}</p>
              )}
            </div>

            {/* Let's not render it for now */}
            {/*<div className="space-y-3">
                <Label className=" font-medium">Theme preference</Label>
                <RadioGroup value={watch("theme")} onValueChange={value => setValue("theme", value)}>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="light" id="light" />
                    <Label
                      htmlFor="light"
                      className={cn(
                        "cursor-pointer font-normal",
                        theme === "light" ? "" : "text-muted-foreground",
                      )}
                    >
                      ☀️ Light
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="dark" id="dark" />
                    <Label
                      htmlFor="dark"
                      className={cn(
                        "cursor-pointer font-normal",
                        theme === "dark" ? "" : "text-muted-foreground",
                      )}
                    >
                      🌙 Dark
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="system" id="system" />
                    <Label
                      htmlFor="system"
                      className={cn(
                        "cursor-pointer font-normal",
                        theme === "system" ? "" : "text-muted-foreground",
                      )}
                    >
                      ⚙️ System
                    </Label>
                  </div>
                </RadioGroup>
              </div>*/}

            <div className="space-y-2">
              <Label className="font-medium">Pick your accent color 🎨</Label>
              <div className="mt-4 grid grid-cols-4 gap-3">
                {colors.map(col => (
                  <button
                    key={col.value}
                    type="button"
                    onClick={() => setValue("color", col.hex)}
                    className={`flex flex-col items-center gap-2 rounded-lg border-2 p-3 transition-all ${
                      color === col.hex
                        ? "border-foreground ring-foreground ring-2 ring-offset-2"
                        : "border-muted hover:border-muted-foreground"
                    }`}
                    title={col.name}
                    disabled={isLoading}
                  >
                    <div
                      className="h-8 w-8 rounded-full shadow-md"
                      style={{ backgroundColor: col.hex }}
                    />
                    <span className="text-muted-foreground text-center text-xs">{col.name}</span>
                  </button>
                ))}
              </div>
              {errors.color && <p className="text-destructive text-sm">{errors.color.message}</p>}
            </div>

            <Button
              type="submit"
              className="w-full rounded-md py-2 font-semibold"
              disabled={isLoading}
            >
              {isLoading ? "Onboarding..." : "Complete Setup ✨"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
