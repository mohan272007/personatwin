import React from "react";

const TYPE_COLORS = {
  conversation: "bg-violet/15 text-violet border-violet/30",
  document: "bg-cyan/15 text-cyan border-cyan/30",
  fact: "bg-amber/15 text-amber border-amber/30",
  preference: "bg-emerald-400/15 text-emerald-300 border-emerald-400/30",
};

export default function MemoryCard({ content, memory_type, created_at, score }) {
  const colorCls = TYPE_COLORS[memory_type] || "bg-muted/15 text-muted border-muted/30";
  const date = created_at ? new Date(created_at).toLocaleString() : "";

  return (
    <div className="glass rounded-xl p-4 hover:border-violet/40 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className={`text-[11px] uppercase tracking-wide font-mono px-2 py-0.5 rounded-full border ${colorCls}`}>
          {memory_type}
        </span>
        <div className="flex items-center gap-2">
          {typeof score === "number" && (
            <span className="text-xs font-mono text-muted">match {(score * 100).toFixed(0)}%</span>
          )}
          <span className="text-xs text-muted">{date}</span>
        </div>
      </div>
      <p className="text-sm text-ink/90 leading-relaxed">{content}</p>
    </div>
  );
}
