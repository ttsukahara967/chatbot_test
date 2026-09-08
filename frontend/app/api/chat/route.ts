export const runtime = "nodejs";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
  const { messages } = await req.json();

  const backendRes = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!backendRes.ok || !backendRes.body) {
    return new Response("Failed to communicate with the backend.", { status: 502 });
  }

  return new Response(backendRes.body, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}
