"use client";

import { UserButton } from "@clerk/nextjs";

export function UserNav() {
  return (
    <div className="relative h-9 w-9 rounded-full">
      <UserButton afterSignOutUrl="/sign-in" />
    </div>
  );
}
