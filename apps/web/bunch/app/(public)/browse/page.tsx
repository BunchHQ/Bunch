"use client"

import { Button } from "@/components/ui/button"
import { useBunches } from "@/lib/hooks"
import { Loader2 } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import BunchCard from "@/components/bunch/BunchCard"

export default function BrowsePage() {
  const router = useRouter()

  // fetch public bunches
  const { bunches, loading, error, fetchBunches } = useBunches(true)

  useEffect(() => {
    fetchBunches()
  }, [fetchBunches])

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="text-primary h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (error) {
    console.error("Failed to fetch public bunches:", error)
    return (
      <div className="flex h-full flex-col items-center justify-center p-8">
        <h1 className="mb-4 text-2xl font-bold">Failed to Fetch Public Bunches</h1>
        <p className="text-muted-foreground mb-6">
          An error occurred while fetching public bunches. Please try again later.
        </p>
        <Button onClick={() => router.push("/app")}>Go Home</Button>
      </div>
    )
  }

  if (!bunches || bunches.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8">
        <h1 className="mb-4 text-2xl font-bold">No Public Bunches yet</h1>
        <p className="text-muted-foreground mb-6">
          There are no public Bunch made yet. Create your own public Bunch
        </p>
        <Button onClick={() => router.push("/app")}>Go Home</Button>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col gap-y-8 p-8">
      <header className="my-4">
        <h1 className="text-2xl font-bold">Public Bunches</h1>
        <p className="text-muted-foreground text-sm">Browse public bunches here and join some</p>
      </header>

      <div className="my-4 grid grid-cols-3 gap-6 px-8">
        {bunches.map(bunch => (
          <Link href={`/app/bunch/${bunch.id}`} key={bunch.id}>
            <BunchCard bunch={bunch} />
          </Link>
        ))}
      </div>
    </div>
  )
}
