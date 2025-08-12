import { NextResponse } from "next/server";

// proxy requests to backend

export async function POST(request: Request, { params }: { params: Promise<{ auth: string[] }> }) {
  const { auth } = await params;
  const endpoint = auth.join("/");

  try {
    const body = await request.json();
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/${endpoint}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Authentication error:", error);
    return NextResponse.json({ error: "Authentication failed" }, { status: 500 });
  }
}
