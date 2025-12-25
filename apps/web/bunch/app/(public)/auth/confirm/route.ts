import { createClient } from "@/lib/supabase/server"
import { type EmailOtpType } from "@supabase/supabase-js"
import { redirect } from "next/navigation"
import { NextResponse, type NextRequest } from "next/server"

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const token_hash = searchParams.get("token_hash")
  const type = searchParams.get("type") as EmailOtpType | null

  const welcomePath = "/onboarding"
  const errorPath = "/auth/error"

  const redirectBaseUrl = process.env.NEXT_PUBLIC_SITE_URL || request.nextUrl.origin

  const createRedirectResponse = (pathname: string): NextResponse => {
    const redirectUrl = new URL(pathname, redirectBaseUrl)
    console.log(`Redirecting to: ${redirectUrl.toString()}`)
    return redirect(redirectUrl.toString())
  }

  if (token_hash && type) {
    const supabase = await createClient()

    const { error } = await supabase.auth.verifyOtp({
      type,
      token_hash,
    })
    if (!error) {
      console.log("Email verification successful.")
      return createRedirectResponse(welcomePath)
    } else {
      console.error("Email verification failed:", error.message)
      return createRedirectResponse(`${errorPath}?error=${error?.message}`)
    }
  }
  console.error("Verification failed: Missing 'token_hash' or 'type' in query parameters.")
  return createRedirectResponse(`${errorPath}?error=No token hash or type`)
}
