/* CSIT Pulse tutor proxy.
 *
 * POST /api/chat  { messages, max_tokens }
 * Streams OpenAI compatible server sent events straight from the provider.
 *
 * Providers, in order:
 *   1. Groq, when GROQ_API_KEY is set on the deployment (free tier, about a
 *      second per answer). Visitors never see this key.
 *   2. Pollinations, which needs no key at all and is the default.
 *
 * Running this on the edge keeps the time to first token low and hides the
 * provider behind our own origin.
 */

export const config = { runtime: "edge" };

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const POLLINATIONS_URL = "https://text.pollinations.ai/openai";
const MAX_TOKENS = 2000;
const MAX_MESSAGES = 12;

function bad(status, message) {
  return new Response(message, {
    status,
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
  });
}

export default async function handler(request) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: { Allow: "POST, OPTIONS" } });
  }
  if (request.method !== "POST") return bad(405, "Use POST.");

  let payload;
  try {
    payload = await request.json();
  } catch {
    return bad(400, "That request was not valid JSON.");
  }

  const messages = Array.isArray(payload?.messages) ? payload.messages.slice(-MAX_MESSAGES) : [];
  if (!messages.length) return bad(400, "Send at least one message.");
  for (const message of messages) {
    if (!message || typeof message.content !== "string" || !message.content.trim()) {
      return bad(400, "Every message needs content.");
    }
  }

  const maxTokens = Math.min(MAX_TOKENS, Math.max(64, Number(payload.max_tokens) || 700));
  const key = process.env.GROQ_API_KEY;

  const upstreamUrl = key ? GROQ_URL : POLLINATIONS_URL;
  const body = key
    ? {
        model: process.env.GROQ_MODEL || "llama-3.3-70b-versatile",
        messages,
        stream: true,
        temperature: 0.35,
        max_tokens: maxTokens,
      }
    : {
        model: "openai",
        messages,
        stream: true,
        temperature: 0.35,
        max_tokens: maxTokens,
        private: true,
      };

  const headers = { "Content-Type": "application/json" };
  if (key) headers.Authorization = `Bearer ${key}`;

  let upstream;
  try {
    upstream = await fetch(upstreamUrl, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  } catch {
    return bad(502, "The model could not be reached.");
  }

  if (!upstream.ok) {
    const text = await upstream.text().catch(() => "");
    return new Response(text || "The model rejected the request.", {
      status: upstream.status === 402 ? 429 : upstream.status,
      headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
    });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-store, no-transform",
      "X-Model": key ? "groq" : "pollinations",
    },
  });
}
