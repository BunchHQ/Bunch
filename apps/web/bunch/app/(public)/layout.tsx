import "@/app/globals.css"
import { SignOutButton } from "@/components/auth/SignOutButton"
import { ThemeProvider } from "@/components/theme/ThemeProvider"
import { ThemeToggle } from "@/components/theme/ThemeToggle"
import { createClient } from "@/lib/supabase/server"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
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
  const { data: authData } = await supabase.auth.getClaims()

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex min-h-screen flex-col">
            <div className="fixed top-4 right-32 z-50">
              <div className="flex flex-row items-center justify-center gap-4">
                <ThemeToggle />
                {authData !== null && <SignOutButton />}
              </div>
            </div>
            <main className="flex flex-1 flex-col">{children}</main>
          </div>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
