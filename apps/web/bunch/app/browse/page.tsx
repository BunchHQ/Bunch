"use client";

import BunchCard from "@/components/bunch/BunchCard";
import { MainLayout } from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { useBunches } from "@/lib/hooks";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function BrowsePage() {
  const router = useRouter();

  // fetch public bunches
  const { bunches, loading, error, fetchBunches } = useBunches(true);

  useEffect(() => {
    fetchBunches();
  }, [fetchBunches]);

  useEffect(() => {
    if (error) {
      console.error("Failed to fetch bunches:", error);
      router.push("/");
    }
  }, [error, router]);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </MainLayout>
    );
  }

  if (!bunches) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center h-full p-8">
          <h1 className="text-2xl font-bold mb-4">No Public Bunches yet</h1>
          <p className="text-muted-foreground mb-6">
            There are no public Bunch made yet. Create your own public Bunch
          </p>
          <Button onClick={() => router.push("/")}>Go Home</Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="flex flex-col h-full p-8 gap-y-8">
        <header className="my-4">
          <h1 className="text-2xl font-bold">Public Bunches</h1>
          <p className="text-sm text-muted-foreground">
            Browse public bunches here and join some
          </p>
        </header>

        <div className="grid grid-cols-3 px-8 my-4 gap-6">
          {bunches.map((bunch) => (
            <Link href={`/bunch/${bunch.id}`} key={bunch.id}>
              <BunchCard bunch={bunch} />
            </Link>
          ))}
        </div>
      </div>
    </MainLayout>
  );
}
