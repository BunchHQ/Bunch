import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Sidebar } from "./Sidebar"

interface MainLayoutProps {
  children: React.ReactNode
}

// MainLayout is supposed to be used in (authenticated) routes only
export async function MainLayout({ children }: MainLayoutProps) {
  const supabase = await createClient()

  const { error } = await supabase.auth.getClaims()
  const isSignedIn = error === null

  if (!isSignedIn) redirect("/auth/sign-in")

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}
