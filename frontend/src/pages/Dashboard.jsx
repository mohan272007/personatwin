import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/api.js";
import MemoryCard from "../components/MemoryCard.jsx";

export default function Dashboard({ user }) {
  const [profile, setProfile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recent, setRecent] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.getProfile(user.user_id).then(setProfile).catch(() => {});
    api.getAnalytics(user.user_id).then(setAnalytics).catch(() => {});
    api.memoryTimeline(user.user_id, 4).then(setRecent).catch(() => {});
  }, [user.user_id]);

  const sampleCount = profile?.personality?.sample_count ?? 0;
  const twinReadiness = Math.min(100, Math.round((sampleCount / 10) * 100));

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-2xl">Hey {user.name?.split(" ")[0] || "there"}, meet your twin.</h1>
        <p className="text-muted text-sm mt-1">
          Here's how much PersonaTwin has learned about you so far.
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        <StatCard label="Twin readiness" value={`${twinReadiness}%`} accent="violet" />
        <StatCard label="Memories stored" value={analytics?.total_memories ?? 0} accent="cyan" />
        <StatCard label="Conversations" value={analytics?.total_conversations ?? 0} accent="amber" />
        <StatCard
          label="Avg. confidence"
          value={analytics ? `${Math.round((analytics.avg_confidence || 0) * 100)}%` : "--"}
          accent="violet"
        />
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <button
          onClick={() => navigate("/chat")}
          className="glass rounded-xl p-5 text-left hover:border-violet/40 transition-colors"
        >
          <p className="text-2xl mb-2">▷</p>
          <p className="font-display">Chat with your twin</p>
          <p className="text-xs text-muted mt-1">Talk to it and watch confidence scores update live.</p>
        </button>
        <button
          onClick={() => navigate("/settings")}
          className="glass rounded-xl p-5 text-left hover:border-cyan/40 transition-colors"
        >
          <p className="text-2xl mb-2">⇪</p>
          <p className="font-display">Teach it more</p>
          <p className="text-xs text-muted mt-1">Upload chats, emails or docs to sharpen its style.</p>
        </button>
        <button
          onClick={() => navigate("/memory")}
          className="glass rounded-xl p-5 text-left hover:border-amber/40 transition-colors"
        >
          <p className="text-2xl mb-2">◈</p>
          <p className="font-display">Browse memory</p>
          <p className="text-xs text-muted mt-1">See everything stored in long-term memory.</p>
        </button>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-display text-lg">Recent memories</h2>
          <button onClick={() => navigate("/memory")} className="text-xs text-violet hover:underline">
            View all →
          </button>
        </div>
        {recent.length === 0 ? (
          <p className="text-sm text-muted glass rounded-xl p-6">
            No memories yet -- start a chat or upload something in Settings to begin.
          </p>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {recent.map((m) => (
              <MemoryCard key={m.id} {...m} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, accent }) {
  const accents = { violet: "text-violet", cyan: "text-cyan", amber: "text-amber" };
  return (
    <div className="glass rounded-xl p-5">
      <p className={`font-display text-3xl ${accents[accent]}`}>{value}</p>
      <p className="text-xs text-muted mt-1">{label}</p>
    </div>
  );
}
