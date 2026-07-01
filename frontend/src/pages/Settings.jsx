import React, { useEffect, useState } from "react";
import { api } from "../api/api.js";

export default function Settings({ user }) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [prefs, setPrefs] = useState([]);
  const [prefKey, setPrefKey] = useState("");
  const [prefValue, setPrefValue] = useState("");

  useEffect(() => {
    api.getPreferences(user.user_id).then(setPrefs).catch(() => {});
  }, [user.user_id]);

  async function submitText() {
    if (!text.trim()) return;
    setBusy(true);
    setStatus("");
    try {
      const res = await api.uploadText(user.user_id, text, "manual_input");
      setStatus(`Learned from ${res.chunks_learned} chunk(s). Personality samples: ${res.personality_profile.sample_count}.`);
      setText("");
    } catch {
      setStatus("Upload failed -- check the backend is running.");
    } finally {
      setBusy(false);
    }
  }

  async function submitFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setStatus("");
    try {
      const res = await api.uploadFile(user.user_id, file, "document");
      setStatus(`Learned from "${file.name}" (${res.chunks_learned} chunk(s)).`);
    } catch {
      setStatus("Upload failed -- check the backend is running.");
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  async function addPreference(e) {
    e.preventDefault();
    if (!prefKey.trim() || !prefValue.trim()) return;
    await api.setPreference(user.user_id, prefKey, prefValue);
    setPrefs(await api.getPreferences(user.user_id));
    setPrefKey("");
    setPrefValue("");
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-2xl">Settings</h1>
        <p className="text-muted text-sm mt-1">Teach your twin and manage permanent preferences.</p>
      </div>

      <section className="glass rounded-xl p-6 space-y-4">
        <h2 className="font-display text-lg">Teach your twin</h2>
        <p className="text-xs text-muted">
          Paste a chat export, email thread, or just write a few sentences the way you normally would.
          The Personality &amp; Communication Style agents learn from this immediately.
        </p>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          placeholder="Hey! Just wanted to say the launch went great, super excited for what's next..."
          className="w-full bg-surface2 border border-border rounded-lg px-3 py-2.5 text-sm outline-none focus:border-violet/60"
        />
        <div className="flex items-center gap-3">
          <button
            onClick={submitText}
            disabled={busy}
            className="bg-violet hover:bg-violet/90 disabled:opacity-60 px-5 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            {busy ? "Learning..." : "Teach twin"}
          </button>
          <label className="px-5 py-2.5 rounded-lg text-sm border border-border cursor-pointer hover:border-cyan/50 transition-colors">
            Upload .txt file
            <input type="file" accept=".txt" onChange={submitFile} className="hidden" />
          </label>
        </div>
        {status && <p className="text-xs text-cyan">{status}</p>}
      </section>

      <section className="glass rounded-xl p-6 space-y-4">
        <h2 className="font-display text-lg">Permanent preferences</h2>
        <p className="text-xs text-muted">
          Facts you want the twin to always remember -- e.g. "coffee_order = oat milk flat white".
        </p>
        <form onSubmit={addPreference} className="flex gap-3">
          <input
            value={prefKey}
            onChange={(e) => setPrefKey(e.target.value)}
            placeholder="key (e.g. coffee_order)"
            className="flex-1 bg-surface2 border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-violet/60"
          />
          <input
            value={prefValue}
            onChange={(e) => setPrefValue(e.target.value)}
            placeholder="value (e.g. oat milk flat white)"
            className="flex-1 bg-surface2 border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-violet/60"
          />
          <button className="bg-surface2 border border-border hover:border-violet/50 px-4 py-2 rounded-lg text-sm transition-colors">
            Add
          </button>
        </form>
        <div className="space-y-2">
          {prefs.length === 0 && <p className="text-xs text-muted">No preferences saved yet.</p>}
          {prefs.map((p) => (
            <div key={p.key} className="flex items-center justify-between text-sm bg-surface2 rounded-lg px-3 py-2">
              <span className="font-mono text-cyan">{p.key}</span>
              <span className="text-ink/80">{p.value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
