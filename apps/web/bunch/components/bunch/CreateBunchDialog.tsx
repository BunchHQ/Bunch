"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { useBunches } from "@/lib/hooks"

const formSchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters"),
  description: z.string().optional(),
  is_private: z.boolean(),
})

type FormData = z.infer<typeof formSchema>

interface CreateBunchDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CreateBunchDialog({
  open,
  onOpenChange,
}: CreateBunchDialogProps) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { createBunch } = useBunches()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
      is_private: false,
    },
  })

  const isPrivate = watch("is_private")

  const onSubmit = async (data: FormData) => {
    setIsLoading(true)

    try {
      const bunch = await createBunch(data)
      toast("Success", {
        description: "Bunch created successfully!",
      })

      reset()
      onOpenChange(false)

      // to the new bunch
      router.push(`/bunch/${bunch.id}`)
    } catch (error) {
      toast("Error", {
        description:
          error instanceof Error ? error.message : "Failed to create bunch",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create a new Bunch</DialogTitle>
          <DialogDescription>
            Create a new server for you and your friends
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              placeholder="Enter bunch name"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="What's this bunch about? (optional)"
              {...register("description")}
            />
          </div>

          <div className="flex items-center justify-between space-x-2">
            <Label htmlFor="is_private">Private Bunch</Label>
            <Switch
              id="is_private"
              checked={isPrivate}
              onCheckedChange={checked => setValue("is_private", checked)}
            />
          </div>

          {isPrivate && (
            <p className="text-sm text-muted-foreground">
              Private bunches require an invite code to join.
            </p>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Creating..." : "Create Bunch"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
