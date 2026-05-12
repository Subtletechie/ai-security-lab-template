// Cloudflare Pages Function: /api/chat
// Lab 1: Prompt validation and basic prompt-injection detection

const MAX_PROMPT_LENGTH = 500;

const INJECTION_PHRASES = [
  "ignore previous instructions",
  "ignore all previous instructions",
  "forget previous instructions",
  "reveal system prompt",
  "show me your system prompt",
  "bypass safety",
  "developer mode",
];

function detectInjection(prompt) {
  const lower = prompt.toLowerCase();
  return INJECTION_PHRASES.some((phrase) => lower.includes(phrase));
}

function logEvent(decision, promptLength, promptPreview, code, requestId) {
  const entry = {
    timestamp: new Date().toISOString(),
    ...(requestId ? { requestId } : {}),
    decision,
    promptLength,
    promptPreview: promptPreview.slice(0, 80),
    ...(code ? { code } : {}),
  };
  console.log("[chat]", JSON.stringify(entry));
}

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export async function onRequest(context) {
  const requestId = context.data.requestId;

  if (context.request.method !== "POST") {
    return json({ status: "error", code: "METHOD_NOT_ALLOWED" }, 405);
  }

  let body;
  try {
    body = await context.request.json();
  } catch {
    return json({ status: "error", code: "INVALID_JSON" }, 400);
  }

  const raw = body && typeof body.prompt === "string" ? body.prompt : "";
  const prompt = raw.trim();

  if (!prompt) {
    logEvent("error", 0, "", "EMPTY_PROMPT", requestId);
    return json({ status: "error", code: "EMPTY_PROMPT" }, 400);
  }

  if (prompt.length > MAX_PROMPT_LENGTH) {
    logEvent("error", prompt.length, prompt, "PROMPT_TOO_LONG", requestId);
    return json(
      { status: "error", code: "PROMPT_TOO_LONG", maxLength: MAX_PROMPT_LENGTH },
      400
    );
  }

  if (detectInjection(prompt)) {
    logEvent("blocked", prompt.length, prompt, "SUSPECTED_PROMPT_INJECTION", requestId);
    return json(
      {
        status: "blocked",
        code: "SUSPECTED_PROMPT_INJECTION",
        reason: "Prompt contains suspicious instruction-manipulation language.",
        timestamp: new Date().toISOString(),
      },
      403
    );
  }

  logEvent("ok", prompt.length, prompt, undefined, requestId);
  return json(
    {
      status: "ok",
      reply: "Mock model response: " + prompt,
      mode: "mock",
      project: "ai-security-lab",
      timestamp: new Date().toISOString(),
    },
    200
  );
}
