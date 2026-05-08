// Cloudflare Pages Function: /api/chat
export async function onRequest(context) {
  if (context.request.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      { status: 405, headers: { "Content-Type": "application/json" } }
    );
  }

  let body;
  try {
    body = await context.request.json();
  } catch {
    return new Response(
      JSON.stringify({ error: "Invalid JSON body" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const prompt = body && typeof body.prompt === "string" ? body.prompt.trim() : "";
  if (!prompt) {
    return new Response(
      JSON.stringify({ error: "Missing or empty prompt" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({
      reply: "Mock model response: " + prompt,
      mode: "mock",
      project: "ai-security-lab",
      timestamp: new Date().toISOString(),
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
