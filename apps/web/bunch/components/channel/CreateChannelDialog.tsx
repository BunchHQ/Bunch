"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Channel } from "@/lib/types";
import { useChannels } from "@/lib/hooks";

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  type: z.enum(["text", "voice", "announcement"]),
  is_private: z.boolean(),
});

type FormData = z.infer<typeof formSchema>;

interface CreateChannelDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  bunchId: string;
  defaultType?: "text" | "voice" | "announcement";
  onSuccess?: (channel: Channel) => void;
}

export function CreateChannelDialog({
  open,
  onOpenChange,
  bunchId,
  defaultType = "text",
  onSuccess,
}: CreateChannelDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { createChannel } = useChannels(bunchId);

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
      type: defaultType,
      is_private: false,
    },
  });

  const isPrivate = watch("is_private");

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);

    try {
      const channel = await createChannel(data);
      toast("Success", { description: "Channel created successfully!" });

      if (onSuccess) {
        onSuccess(channel);
      }
      reset();
      onOpenChange(false);

      // to the new channel
      router.push(`/bunch/${bunchId}/channel/${channel.id}`);
    } catch (error) {
      toast("Error", {
        description:
          error instanceof Error ? error.message : "Failed to create channel",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create Channel</DialogTitle>
          <DialogDescription>Add a new channel to your bunch</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="type">Channel Type</Label>
            <Select
              defaultValue={defaultType}
              onValueChange={(value) =>
                setValue("type", value as "text" | "voice" | "announcement")
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a channel type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text Channel</SelectItem>
                <SelectItem value="voice">Voice Channel</SelectItem>
                <SelectItem value="announcement">Announcement</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Channel Name</Label>
            <Input
              id="name"
              placeholder="Enter channel name"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              placeholder="What's this channel for?"
              {...register("description")}
            />
          </div>

          <div className="flex items-center justify-between space-x-2">
            <div>
              <Label htmlFor="is_private" className="block">
                Private Channel
              </Label>
              <p className="text-sm text-muted-foreground">
                Only certain members will be able to view this channel
              </p>
            </div>
            <Switch
              id="is_private"
              checked={isPrivate}
              onCheckedChange={(checked) => setValue("is_private", checked)}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Creating..." : "Create Channel"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
