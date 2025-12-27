import { createServerClient } from "@supabase/ssr"
import { NextResponse, type NextRequest } from "next/server"

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  })

  // With Fluid compute, don't put this client in a global environment
  // variable. Always create a new one on each request.
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({
            request,
          })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          )
        },
      },
    },
  )

  // Do not run code between createServerClient and
  // supabase.auth.getClaims(). A simple mistake could make it very hard to debug
  // issues with users being randomly logged out.

  // IMPORTANT: If you remove getClaims() and you use server-side rendering
  // with the Supabase client, your users may be randomly logged out.
  const { data } = await supabase.auth.getClaims()

  const user = data?.claims
  const pathname = request.nextUrl.pathname

  const isAuthRoute = pathname.startsWith("/auth")
  const isAppRoute = pathname.startsWith("/app")
  const isBrowseRoute = pathname.startsWith("/browse")
  const isOnboardingRoute = pathname === "/onboarding"
  const isHomeRoute = pathname === "/"

  const isPublicRoute = isHomeRoute || isBrowseRoute || isAuthRoute

  if (!user && !isPublicRoute) {
    console.debug(
      "No user found, but tried to access a protected route, redirecting to /auth/sign-in",
    )
    const url = request.nextUrl.clone()
    url.pathname = "/auth/sign-in"
    return NextResponse.redirect(url)
  }

  if (user && (user.user_metadata?.onboarded ?? false) == false && !isOnboardingRoute) {
    // onboarding is not completed, redirect to onboarding first
    console.debug("User is not onboarded, redirecting to /onboarding")
    const url = request.nextUrl.clone()
    url.pathname = "/onboarding"
    return NextResponse.redirect(url)
  }

  if (user && (user.user_metadata?.onboarded ?? false) == true && isOnboardingRoute) {
    // onboarding is completed, redirect to app
    console.debug("User is onboarded, redirecting to /app")
    const url = request.nextUrl.clone()
    url.pathname = "/app"
    return NextResponse.redirect(url)
  }

  if (user && (isAuthRoute || isHomeRoute)) {
    // user is logged in, but trying to access auth or /
    console.debug("User is logged in, but accessing unprotected routes, redirecting to /app")
    const url = request.nextUrl.clone()
    url.pathname = "/app"
    return NextResponse.redirect(url)
  }

  // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
  // creating a new response object with NextResponse.next() make sure to:
  // 1. Pass the request in it, like so:
  //    const myNewResponse = NextResponse.next({ request })
  // 2. Copy over the cookies, like so:
  //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
  // 3. Change the myNewResponse object to fit your needs, but avoid changing
  //    the cookies!
  // 4. Finally:
  //    return myNewResponse
  // If this is not done, you may be causing the browser and server to go out
  // of sync and terminate the user's session prematurely!

  return supabaseResponse
}
