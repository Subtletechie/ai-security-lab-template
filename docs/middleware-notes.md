# Middleware Notes

## What `functions/_middleware.js` does

`functions/_middleware.js` is a Cloudflare Pages middleware file that runs automatically before every route handler under `/functions`. For each incoming request it:

1. Generates a unique **request ID** (`crypto.randomUUID()`).
2. Records the **start time** in milliseconds.
3. Writes a structured **request log** line: `requestId`, `method`, `pathname`, `timestamp`.
4. Stores the `requestId` in `context.data` so downstream handlers (e.g. `chat.js`) can reference it in their own log lines.
5. Calls `context.next()` to hand off to the matched route handler.
6. After the response comes back, calculates **elapsed time** and logs the response status.
7. Attaches two headers to every response:
   - `X-Request-Id` — the UUID for this request
   - `X-App-Name: ai-security-lab`

## Why middleware is useful here

Without middleware every route would have to repeat the same boilerplate: generating IDs, timing requests, adding headers. Middleware keeps that logic in one place. Any new route you add automatically gets request tracing and consistent response headers for free.

## How it supports later modules

As the lab grows, `_middleware.js` is the right place to add cross-cutting concerns:

| Future module | Where it fits |
|---|---|
| Rate limiting | Check a counter in middleware before calling `next()` |
| Prompt pre-filtering | Inspect the request body in middleware, reject early |
| Sensitive-data redaction | Wrap the response body from `next()` and scrub it |
| Policy enforcement | Read policy rules and block requests before they reach handlers |
| Centralised audit logging | One log sink in middleware, consistent across all routes |

## Request flow

```
Browser request
     │
     ▼
functions/_middleware.js   ← generates requestId, logs request
     │
     │  context.next()
     ▼
functions/api/chat.js      ← validates prompt, detects injection, logs with requestId
  or
functions/api/health.js    ← returns status
     │
     ▼
functions/_middleware.js   ← logs response status + elapsed ms, adds X-Request-Id header
     │
     ▼
Browser response
```

## Key implementation detail

Cloudflare Pages middleware passes a `context` object. Setting `context.data.requestId` in middleware makes that value readable in any downstream handler as `context.data.requestId`. No globals, no imports needed.
