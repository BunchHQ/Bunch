import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, MessageCircle, Users, Zap } from "lucide-react"
import Link from "next/link"

// The Public "Home" page
export default function Home() {
  return (
    <div className="flex h-full min-h-svh flex-col items-center justify-center p-8">
      <div className="mb-12 w-full max-w-4xl text-center">
        <h1 className="from-primary to-primary/60 mb-4 bg-linear-to-r bg-clip-text text-5xl font-bold text-transparent">
          Welcome to Bunch
        </h1>
        <p className="text-muted-foreground mb-8 text-lg">
          Chat platform for any kind of groups. Join bunches, create channels, and chat in
          real-time.
        </p>
        <div className="flex justify-center gap-4">
          <Link href="/auth/sign-in">
            <Button size="lg" variant="default">
              Sign In
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/auth/sign-up">
            <Button size="lg" variant="outline">
              Create Account
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid w-full max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="transition-all hover:-translate-y-1 hover:shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-xl">
              <MessageCircle className="text-primary mr-2 h-6 w-6" />
              Start Chatting
            </CardTitle>
            <CardDescription>Join a bunch and start a conversation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground text-sm">Sign in to join bunches</p>
            <Link href="/auth/sign-in">
              <Button variant="ghost" size="sm" className="w-full">
                Get Started
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="transition-all hover:-translate-y-1 hover:shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-xl">
              <Users className="text-primary mr-2 h-6 w-6" />
              Create a Bunch
            </CardTitle>
            <CardDescription>Start your own community with friends</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground text-sm">Sign in to create your own bunch</p>
            <Link href="/auth/sign-in">
              <Button variant="ghost" size="sm" className="w-full">
                Get Started
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="transition-all hover:-translate-y-1 hover:shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-xl">
              <Zap className="text-primary mr-2 h-6 w-6" />
              Browse Bunches
            </CardTitle>
            <CardDescription>Discover public bunches and communities</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground text-sm">Explore public bunches</p>
            <Link href="/browse">
              <Button variant="ghost" size="sm" className="w-full">
                Browse Bunches
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
