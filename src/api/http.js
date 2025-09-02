// src/api/http.js
export async function apiPost(path, body, base = window.API_BASE || "http://localhost:5000") {
  const initData = window.Telegram?.WebApp?.initData || "";
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}