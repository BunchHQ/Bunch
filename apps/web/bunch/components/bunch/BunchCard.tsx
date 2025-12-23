import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { Bunch } from "@/lib/types"
import { Users2 } from "lucide-react"
import Image from "next/image"

interface BunchCardProps {
  bunch: Bunch
}

export default function BunchCard({ bunch }: BunchCardProps) {
  return (
    <Card className="pt-0">
      <CardHeader
        className="rounded-xl rounded-b-none bg-linear-to-l from-(--bunch-primary-color)/25 to-transparent py-6"
        style={
          {
            "--bunch-primary-color": bunch.primary_color,
          } as React.CSSProperties
        }
      >
        <Image
          className="mb-2"
          src={bunch.icon || "/favicon.ico"}
          alt={`Icon for bunch ${bunch.id}`}
          width={40}
          height={40}
        />
        <CardTitle>{bunch.name}</CardTitle>
        <CardDescription>{bunch.description || "No Description"}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div className="flex flex-row items-center justify-start gap-2">
          <div className="h-2 w-2 animate-pulse rounded-full bg-green-500 ring-4 ring-green-400/30" />
          3939 Members online
        </div>
        <p className="flex flex-row items-center justify-start gap-2">
          <Users2 size={18} /> {bunch.members_count} Total Members
        </p>
      </CardContent>
      <CardFooter>
        <p className="text-muted-foreground">created on: {bunch.created_at}</p>
      </CardFooter>
    </Card>
  )
}
