"use client";

import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { useBunches } from "@/lib/hooks";
import { useUser } from "@clerk/nextjs";
import { Loader2 } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Sidebar } from "./Sidebar";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { isLoaded, isSignedIn } = useUser();
  const { bunches, loading, fetchBunches } = useBunches();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (isSignedIn) {
      fetchBunches();
    }
  }, [isSignedIn, fetchBunches]);

  // Public routes don't need the sidebar
  if (pathname === "/sign-in" || pathname === "/sign-up") {
    return (
      <div className="flex min-h-screen flex-col">
        <div className="fixed top-4 right-4 z-50">
          <ThemeToggle />
        </div>
        <main className="flex-1 flex items-center justify-center p-4">
          {children}
        </main>
      </div>
    );
  }

  if (!isLoaded || (isSignedIn && loading)) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  // authenticated routes, show sidebar
  return (
    <div className="flex h-screen overflow-hidden">
      {isSignedIn && <Sidebar bunches={bunches} />}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
