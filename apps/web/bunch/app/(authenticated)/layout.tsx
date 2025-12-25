import "@/app/globals.css"
import { MainLayout } from "@/components/layout/MainLayout"
import { ThemeProvider } from "@/components/theme/ThemeProvider"
import { createClient } from "@/lib/supabase/server"
import { WebSocketProvider } from "@/lib/WebSocketProvider"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { redirect } from "next/navigation"
import { Toaster } from "sonner"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Bunch - Modern Chat App",
  description: "Very cool",
  appleWebApp: {
    title: "Bunch",
  },
  applicationName: "Bunch",
  authors: [
    { name: "tomlin7", url: "https://github.com/tomlin7" },
    { name: "HarshNarayanJha", url: "https://github.com/HarshNarayanJha" },
  ],
  creator: "Bunch HQ",
  keywords: ["Messaging", "Cross Platform", "Bunch"],
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient()

  const { data, error } = await supabase.auth.getClaims()
  if (error || !data?.claims) {
    redirect("/auth/sign-in")
  }

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <WebSocketProvider>
            <main>
              <MainLayout>{children}</MainLayout>
            </main>
            <Toaster />
          </WebSocketProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
