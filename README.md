# AI Security Lab Template

Template repo for an AI Security Engineering lab using Cloudflare Pages and Pages Functions.

## Structure

```
app/
  index.html   – Main HTML entry point
  app.js       – Application logic
  styles.css   – Base styles
functions/
  api/
    health.js  – Health check endpoint (/api/health)
README.md
```

## Deployment

Deploy via Cloudflare Pages. No build step required — set the root directory as the publish directory.

## API Endpoints

| Endpoint | Description |
|---|---|
| `/api/health` | Returns `{ "status": "ok", "timestamp": "..." }` |
