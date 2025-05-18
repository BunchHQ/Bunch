import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import { WebSocketProvider } from "@/lib/WebSocketProvider";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { ClerkProvider } from "@clerk/nextjs";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Bunch - Modern Chat App",
  description: "Very cool",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
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
  );
}
