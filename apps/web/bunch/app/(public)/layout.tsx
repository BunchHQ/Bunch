import "@/app/globals.css"
import { ThemeProvider } from "@/components/theme/ThemeProvider"
import { ThemeToggle } from "@/components/theme/ThemeToggle"
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

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex min-h-screen flex-col">
            <div className="fixed top-4 right-4 z-50">
              <ThemeToggle />
            </div>
            <main className="flex flex-1 items-center justify-center p-4">{children}</main>
          </div>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
