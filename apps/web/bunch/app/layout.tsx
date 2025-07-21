import { ClerkProvider } from "@clerk/nextjs"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Toaster } from "sonner"
import { ThemeProvider } from "@/components/theme/ThemeProvider"
import { WebSocketProvider } from "@/lib/WebSocketProvider"
import "./globals.css"

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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className={inter.className}>
          <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
            <WebSocketProvider>
              <main>{children}</main>
              <Toaster />
            </WebSocketProvider>
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  )
}
