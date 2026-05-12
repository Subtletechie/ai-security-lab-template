// Cloudflare Pages Middleware: runs before every route under /functions
// Adds request tracing, structured logging, and common response headers.

export async function onRequest(context) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const { method, url } = context.request;
  const { pathname } = new URL(url);

  // Make the request ID available to downstream handlers via context.data
  context.data.requestId = requestId;

  console.log(
    "[middleware] request",
    JSON.stringify({ requestId, method, pathname, timestamp: new Date().toISOString() })
  );

  // Hand off to the matching route handler
  const response = await context.next();

  const elapsed = Date.now() - startTime;

  console.log(
    "[middleware] response",
    JSON.stringify({ requestId, status: response.status, elapsedMs: elapsed })
  );

  // Attach tracing headers to every response
  const headers = new Headers(response.headers);
  headers.set("X-Request-Id", requestId);
  headers.set("X-App-Name", "ai-security-lab");

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
