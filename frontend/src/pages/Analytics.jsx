import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../api/api.js";

export default function Analytics({ user }) {
  const [data, setData] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    api.getAnalytics(user.user_id).then(setData);
    api.getAgentLogs(user.user_id, 40).then(setLogs);
  }, [user.user_id]);

  if (!data) return <div className="p-8 text-sm text-muted">Loading analytics...</div>;

  const trend = data.confidence_trend.map((t) => ({ turn: t.turn, confidence: Math.round(t.confidence * 100) }));

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-2xl">Analytics</h1>
        <p className="text-muted text-sm mt-1">How your twin is learning, turn by turn.</p>
      </div>

      <section className="glass rounded-xl p-6">
        <h2 className="font-display text-lg mb-4">Confidence score over time</h2>
        {trend.length === 0 ? (
          <p className="text-sm text-muted">Chat with your twin to start seeing a trend.</p>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={trend}>
              <CartesianGrid stroke="#232B42" strokeDasharray="3 3" />
              <XAxis dataKey="turn" stroke="#8791A8" fontSize={12} label={{ value: "turn", position: "insideBottom", offset: -3, fill: "#8791A8", fontSize: 11 }} />
              <YAxis stroke="#8791A8" fontSize={12} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#121726", border: "1px solid #232B42", borderRadius: 8, fontSize: 12 }} />
              <Line type="monotone" dataKey="confidence" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 3, fill: "#22D3EE" }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </section>

      <div className="grid md:grid-cols-2 gap-4">
        <section className="glass rounded-xl p-6">
          <h2 className="font-display text-lg mb-4">Memory type breakdown</h2>
          {Object.entries(data.memory_type_breakdown).length === 0 ? (
            <p className="text-sm text-muted">No memories yet.</p>
          ) : (
            <div className="space-y-3">
              {Object.entries(data.memory_type_breakdown).map(([type, count]) => (
                <BarRow key={type} label={type} value={count} max={Math.max(...Object.values(data.memory_type_breakdown))} />
              ))}
            </div>
          )}
        </section>

        <section className="glass rounded-xl p-6">
          <h2 className="font-display text-lg mb-4">Agent activity</h2>
          {Object.entries(data.agent_activity_counts).length === 0 ? (
            <p className="text-sm text-muted">No agent activity logged yet.</p>
          ) : (
            <div className="space-y-3">
              {Object.entries(data.agent_activity_counts).map(([agent, count]) => (
                <BarRow key={agent} label={agent} value={count} max={Math.max(...Object.values(data.agent_activity_counts))} color="cyan" />
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="glass rounded-xl p-6">
        <h2 className="font-display text-lg mb-3">Top topics in memory</h2>
        <div className="flex gap-2 flex-wrap">
          {data.top_topics.length === 0 && <p className="text-sm text-muted">Nothing learned yet.</p>}
          {data.top_topics.map((t) => (
            <span key={t.topic} className="text-xs font-mono bg-surface2 border border-border rounded-full px-3 py-1.5">
              {t.topic} <span className="text-muted">×{t.count}</span>
            </span>
          ))}
        </div>
      </section>

      <section className="glass rounded-xl p-6">
        <h2 className="font-display text-lg mb-3">Agent activity logs</h2>
        <div className="max-h-80 overflow-y-auto space-y-1.5 font-mono text-xs">
          {logs.length === 0 && <p className="text-muted">No logs yet -- send a chat message first.</p>}
          {logs.map((l) => (
            <div key={l.id} className="flex items-center gap-3 bg-surface2 rounded-lg px-3 py-2">
              <span className="text-violet w-40 shrink-0 truncate">{l.agent_name}</span>
              <span className="text-cyan w-32 shrink-0 truncate">{l.action}</span>
              <span className="text-muted truncate flex-1">{l.detail}</span>
              <span className="text-muted shrink-0">{l.duration_ms.toFixed(1)}ms</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function BarRow({ label, value, max, color = "violet" }) {
  const pct = max ? (value / max) * 100 : 0;
  const colorCls = color === "cyan" ? "from-cyan to-violet" : "from-violet to-cyan";
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-muted capitalize">{label}</span>
        <span className="font-mono text-ink/70">{value}</span>
      </div>
      <div className="h-2 rounded-full bg-surface2 overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${colorCls}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
