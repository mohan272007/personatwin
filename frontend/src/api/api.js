const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export const api = {
  mockLogin: (email, name) =>
    request(`/auth/google/mock?email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}`, {
      method: "POST",
    }),

  chat: (user_id, message) =>
    request(`/chat`, { method: "POST", body: JSON.stringify({ user_id, message }) }),

  uploadText: (user_id, text, source = "manual_input") =>
    request(`/upload/text`, { method: "POST", body: JSON.stringify({ user_id, text, source }) }),

  uploadFile: async (user_id, file, source = "document") => {
    const form = new FormData();
    form.append("user_id", user_id);
    form.append("source", source);
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/upload/file`, { method: "POST", body: form });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },

  searchMemory: (user_id, q, top_k = 5) =>
    request(`/memory/search?user_id=${encodeURIComponent(user_id)}&q=${encodeURIComponent(q)}&top_k=${top_k}`),

  memoryTimeline: (user_id, limit = 100) =>
    request(`/memory/timeline?user_id=${encodeURIComponent(user_id)}&limit=${limit}`),

  getProfile: (user_id) => request(`/profile?user_id=${encodeURIComponent(user_id)}`),

  updateProfile: (payload) => request(`/profile`, { method: "POST", body: JSON.stringify(payload) }),

  getPreferences: (user_id) => request(`/preferences?user_id=${encodeURIComponent(user_id)}`),

  setPreference: (user_id, key, value) =>
    request(`/preferences`, { method: "POST", body: JSON.stringify({ user_id, key, value }) }),

  getAnalytics: (user_id) => request(`/analytics?user_id=${encodeURIComponent(user_id)}`),

  getAgentLogs: (user_id, limit = 50) =>
    request(`/analytics/logs?user_id=${encodeURIComponent(user_id)}&limit=${limit}`),
};
