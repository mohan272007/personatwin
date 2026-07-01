import React from "react";
import { useNavigate } from "react-router-dom";
import ConstellationCanvas from "../components/ConstellationCanvas.jsx";

const FEATURES = [
  { title: "Learns your voice", desc: "Upload chats, emails or documents -- the twin picks up your tone, phrasing and habits." },
  { title: "Remembers everything", desc: "Long-term semantic memory in Qdrant means it recalls context from weeks ago, instantly." },
  { title: "Knows what it doesn't know", desc: "A live Confidence Score flags low-certainty answers and asks before it guesses." },
  { title: "Explains itself", desc: "Every reply shows exactly which memories and traits shaped it -- no black box." },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <header className="max-w-6xl mx-auto flex items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet to-cyan flex items-center justify-center font-display font-bold">P</div>
          <span className="font-display font-semibold tracking-tight">PersonaTwin AI</span>
        </div>
        <button
          onClick={() => navigate("/login")}
          className="text-sm px-4 py-2 rounded-lg border border-border hover:border-violet/50 transition-colors"
        >
          Sign in
        </button>
      </header>

      <section className="relative max-w-6xl mx-auto px-6 pt-16 pb-24">
        <div className="absolute inset-0 -z-10 opacity-70 h-[520px]">
          <ConstellationCanvas nodeCount={48} />
        </div>

        <p className="font-mono text-xs text-cyan tracking-widest uppercase mb-4">
          Multi-agent digital twin · Gemini + Qdrant + A2A
        </p>
        <h1 className="font-display text-5xl md:text-6xl font-semibold leading-[1.05] max-w-3xl">
          A digital twin that answers <span className="text-violet">exactly like you</span> --
          and tells you when it isn't sure.
        </h1>
        <p className="text-muted text-lg mt-6 max-w-2xl">
          PersonaTwin learns your personality, tone and memories from real conversations,
          then responds in your voice -- backed by a transparent Confidence Score instead
          of confident-sounding guesses.
        </p>
        <div className="flex items-center gap-4 mt-9">
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-3 rounded-lg bg-violet hover:bg-violet/90 font-medium shadow-glow transition-colors"
          >
            Launch your twin
          </button>
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-3 rounded-lg border border-border hover:border-cyan/50 transition-colors text-sm"
          >
            See it in action →
          </button>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-12">
        <div className="grid md:grid-cols-2 gap-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="glass rounded-xl p-6">
              <h3 className="font-display text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-24">
        <div className="glass rounded-2xl p-8 grid md:grid-cols-4 gap-6 text-center">
          {[
            ["6", "specialized agents"],
            ["A2A", "message protocol"],
            ["Qdrant", "semantic memory"],
            ["Live", "confidence score"],
          ].map(([big, small]) => (
            <div key={small}>
              <p className="font-display text-3xl text-violet">{big}</p>
              <p className="text-xs text-muted uppercase tracking-wide mt-1">{small}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="max-w-6xl mx-auto px-6 pb-10 text-xs text-muted">
        Built for the AI Hackathon · PersonaTwin AI
      </footer>
    </div>
  );
}
