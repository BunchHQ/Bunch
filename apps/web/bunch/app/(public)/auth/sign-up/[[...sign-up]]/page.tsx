import { SignUpForm } from "@/components/auth/SignUpForm"
import Image from "next/image"

export default function Page() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          <Image src="/icon1.png" width={48} height={48} alt="" />
          <h1 className="text-2xl font-bold">Bunch</h1>
          <p className="text-muted-foreground mt-2 text-center text-sm">
            Create your account to get started
          </p>
        </div>
        <SignUpForm />
      </div>
    </div>
  )
}
