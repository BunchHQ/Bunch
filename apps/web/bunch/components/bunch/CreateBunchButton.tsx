"use client"

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
import { zodResolver } from "@hookform/resolvers/zod"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

const formSchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters"),
  description: z.string().optional(),
  is_private: z.boolean(),
})

type FormData = z.infer<typeof formSchema>

interface CreateBunchButtonProps {
  className?: string
  children?: React.ReactNode
}

/**
 * CreateBunchButton component
 *
 * @param className - CSS class name to apply to the default button. Ignored if children is provided.
 * @param children - Custom content to render instead of the default button. If provided, replaces the default button entirely.
 */
export function CreateBunchButton({ className, children }: CreateBunchButtonProps) {
  const [dialogOpen, setDialogOpen] = useState(false)
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
      setDialogOpen(false)

      // to the new bunch
      router.push(`/app/bunch/${bunch.id}`)
    } catch (error) {
      toast("Error", {
        description: error instanceof Error ? error.message : "Failed to create bunch",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      {children ? (
        <div onClick={() => setDialogOpen(true)} className="contents">
          {children}
        </div>
      ) : (
        <Button className={className} onClick={() => setDialogOpen(true)}>
          Create Bunch
        </Button>
      )}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-106.25">
          <DialogHeader>
            <DialogTitle>Create a new Bunch</DialogTitle>
            <DialogDescription>Create a new server for you and your friends</DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="Enter bunch name" {...register("name")} />
              {errors.name && <p className="text-destructive text-sm">{errors.name.message}</p>}
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
              <p className="text-muted-foreground text-sm">
                Private bunches require an invite code to join.
              </p>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Bunch"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}
