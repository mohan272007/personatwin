import React, { useEffect, useState } from "react";
import { api } from "../api/api.js";

const TRAIT_LABELS = {
  openness: "Openness",
  conscientiousness: "Conscientiousness",
  extraversion: "Extraversion",
  agreeableness: "Agreeableness",
  sociability: "Sociability",
};

export default function Profile({ user }) {
  const [profile, setProfile] = useState(null);
  const [name, setName] = useState(user.name || "");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getProfile(user.user_id).then(setProfile);
  }, [user.user_id]);

  async function saveName() {
    await api.updateProfile({ user_id: user.user_id, name, email: user.email });
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  if (!profile) return <div className="p-8 text-sm text-muted">Loading profile...</div>;

  const traits = profile.personality?.traits || {};

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-2xl">Profile</h1>
        <p className="text-muted text-sm mt-1">
          What PersonaTwin has learned about you, in one place.
        </p>
      </div>

      <section className="glass rounded-xl p-6 space-y-4">
        <h2 className="font-display text-lg">Basic info</h2>
        <div className="flex gap-3 items-center">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="flex-1 bg-surface2 border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-violet/60"
          />
          <button
            onClick={saveName}
            className="bg-violet hover:bg-violet/90 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            {saved ? "Saved ✓" : "Save"}
          </button>
        </div>
        <p className="text-xs text-muted">{user.email}</p>
      </section>

      <section className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg">Personality traits</h2>
          <span className="text-xs text-muted font-mono">
            learned from {profile.personality?.sample_count ?? 0} sample(s)
          </span>
        </div>
        <div className="space-y-3">
          {Object.entries(TRAIT_LABELS).map(([key, label]) => {
            const value = traits[key] ?? 0;
            return (
              <div key={key}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted">{label}</span>
                  <span className="font-mono text-ink/70">{Math.round(value * 100)}%</span>
                </div>
                <div className="h-2 rounded-full bg-surface2 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-violet to-cyan"
                    style={{ width: `${Math.min(100, value * 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-3 gap-4 pt-2">
          <MiniStat label="Formality" value={`${Math.round((profile.personality?.formality_score ?? 0.5) * 100)}%`} />
          <MiniStat label="Positivity" value={`${Math.round((profile.personality?.positivity_score ?? 0.5) * 100)}%`} />
          <MiniStat label="Avg. sentence" value={`${Math.round(profile.personality?.avg_sentence_length ?? 12)} words`} />
        </div>
      </section>

      <section className="glass rounded-xl p-6 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg">Opinions &amp; values</h2>
          <span className="text-xs text-muted font-mono">
            {profile.personality?.values?.length ?? 0} learned
          </span>
        </div>
        <p className="text-xs text-muted">
          Statements the twin extracted from your own words (e.g. "I love...",
          "I think...") -- it uses these as its own stance when relevant.
        </p>
        {(!profile.personality?.values || profile.personality.values.length === 0) ? (
          <p className="text-sm text-muted">
            Nothing learned yet. Try writing things like "I love hiking" or
            "I think remote work is better" in Settings.
          </p>
        ) : (
          <div className="space-y-2">
            {profile.personality.values.map((v, i) => (
              <div key={i} className="flex items-start gap-3 bg-surface2 rounded-lg px-3 py-2">
                <span
                  className={`text-[10px] uppercase tracking-wide font-mono px-2 py-0.5 rounded-full border shrink-0 mt-0.5 ${
                    v.sentiment > 0.3
                      ? "text-emerald-300 border-emerald-400/30 bg-emerald-400/10"
                      : v.sentiment < -0.3
                      ? "text-red-400 border-red-400/30 bg-red-400/10"
                      : "text-cyan border-cyan/30 bg-cyan/10"
                  }`}
                >
                  {v.category}
                </span>
                <p className="text-sm text-ink/90">{v.statement}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="glass rounded-xl p-6 space-y-3">
        <h2 className="font-display text-lg">Communication style</h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-xs text-muted mb-1">Tone</p>
            <p className="capitalize">{profile.style?.tone || "neutral"}</p>
          </div>
          <div>
            <p className="text-xs text-muted mb-1">Greeting style</p>
            <p>{profile.style?.greeting_style || "Hi"}</p>
          </div>
          <div>
            <p className="text-xs text-muted mb-1">Sign-off style</p>
            <p>{profile.style?.sign_off_style || "--"}</p>
          </div>
          <div>
            <p className="text-xs text-muted mb-1">Punctuation</p>
            <p className="capitalize">{profile.style?.punctuation_style || "standard"}</p>
          </div>
        </div>
        {profile.style?.common_phrases?.length > 0 && (
          <div>
            <p className="text-xs text-muted mb-2 mt-2">Frequently used phrases</p>
            <div className="flex gap-2 flex-wrap">
              {profile.style.common_phrases.map((p) => (
                <span key={p} className="text-xs font-mono bg-surface2 border border-border rounded-full px-3 py-1">
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div className="bg-surface2 rounded-lg p-3 text-center">
      <p className="font-display text-lg">{value}</p>
      <p className="text-[11px] text-muted">{label}</p>
    </div>
  );
}
