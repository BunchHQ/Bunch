"use client"

// import { useUser } from "@clerk/nextjs";
import { Hash, MessageCircle, Settings, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { CreateBunchDialog } from "@/components/bunch/CreateBunchDialog"
import { MainLayout } from "@/components/layout/MainLayout"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function Home() {
  // const { isLoaded, isSignedIn } = useUser();
  const router = useRouter()

  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  // useEffect(() => {
  //   if (isLoaded && !isSignedIn) {
  //     router.push("/sign-in");
  //   }
  // }, [isLoaded, isSignedIn, router]);

  // if (!isLoaded || !isSignedIn) {
  //   return null;
  // }

  return (
    <MainLayout>
      <div className="flex h-full flex-col items-center justify-center p-8">
        <div className="mb-8 w-full max-w-4xl text-center">
          <h1 className="mb-4 text-4xl font-bold">Welcome to Bunch</h1>
          <p className="text-muted-foreground text-lg">
            Chat platform for any kind of groups. Join bunches, create channels,
            and chat in real-time.
          </p>
        </div>

        <div className="grid w-full max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="transition-all hover:shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center">
                <MessageCircle className="text-primary mr-2 h-5 w-5" />
                Start Chatting
              </CardTitle>
              <CardDescription>
                Join a bunch and start a conversation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" onClick={() => router.push("/browse")}>
                Browse Bunches
              </Button>
            </CardContent>
          </Card>

          <Card className="transition-all hover:shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center">
                <Users className="text-primary mr-2 h-5 w-5" />
                Create a Bunch
              </CardTitle>
              <CardDescription>
                Start your own community with friends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => setCreateDialogOpen(true)}
              >
                Create Bunch
              </Button>
            </CardContent>
          </Card>

          <Card className="transition-all hover:shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center">
                <Hash className="text-primary mr-2 h-5 w-5" />
                Join with Code
              </CardTitle>
              <CardDescription>
                Join a private bunch with an invite code
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => router.push("/bunch/join")}
              >
                Join Bunch
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8">
          <Button variant="ghost" onClick={() => router.push("/settings")}>
            <Settings className="mr-2 h-4 w-4" />
            Account Settings
          </Button>
        </div>
      </div>

      <CreateBunchDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </MainLayout>
  )
}
