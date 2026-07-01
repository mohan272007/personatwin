import React, { useEffect, useRef, useState } from "react";
import { api } from "../api/api.js";
import ConfidenceBadge from "../components/ConfidenceBadge.jsx";

export default function Chat({ user }) {
  const [messages, setMessages] = useState([
    {
      role: "twin",
      text: "Hi! I'm your digital twin -- still learning. Chat with me, or upload some of your writing in Settings so I can sound more like you.",
      confidence: null,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState({});
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const result = await api.chat(user.user_id, text);
      setMessages((m) => [
        ...m,
        {
          role: "twin",
          text: result.needs_clarification ? result.clarification_question : result.response,
          confidence: result.confidence_score,
          explanation: result.explanation,
          memories_used: result.memories_used,
          needs_clarification: result.needs_clarification,
        },
      ]);
    } catch (err) {
      setMessages((m) => [...m, { role: "twin", text: "Backend unreachable -- check that FastAPI is running on :8000.", confidence: 0 }]);
    } finally {
      setLoading(false);
    }
  }

  function toggleExplain(idx) {
    setExpanded((e) => ({ ...e, [idx]: !e[idx] }));
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="border-b border-border px-8 py-4 flex items-center justify-between">
        <div>
          <h1 className="font-display text-lg">Chat with your twin</h1>
          <p className="text-xs text-muted">Every reply is scored for how confidently it reflects you.</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4 max-w-3xl w-full mx-auto">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] ${m.role === "user" ? "" : "w-full"}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-violet text-white rounded-br-sm"
                    : `glass rounded-bl-sm ${m.needs_clarification ? "border-amber/40" : ""}`
                }`}
              >
                {m.text}
              </div>

              {m.role === "twin" && m.confidence !== null && (
                <div className="mt-2 flex items-center gap-2 flex-wrap">
                  <ConfidenceBadge score={m.confidence} size="sm" />
                  {m.explanation && (
                    <button
                      onClick={() => toggleExplain(idx)}
                      className="text-xs text-muted hover:text-cyan underline underline-offset-2"
                    >
                      {expanded[idx] ? "Hide reasoning" : "Why this response?"}
                    </button>
                  )}
                </div>
              )}

              {expanded[idx] && (
                <div className="mt-2 glass rounded-lg p-3 text-xs text-muted space-y-2">
                  <p>{m.explanation}</p>
                  {m.memories_used?.length > 0 && (
                    <div className="space-y-1">
                      <p className="text-ink/80 font-medium">Memories used:</p>
                      {m.memories_used.map((mem) => (
                        <p key={mem.id} className="font-mono text-[11px] text-muted/90">
                          · [{(mem.score * 100).toFixed(0)}%] {mem.content.slice(0, 90)}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="glass rounded-2xl rounded-bl-sm px-4 py-3 w-fit text-sm text-muted">
            <span className="animate-pulse">Agents are thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border px-8 py-4">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Say something to your twin..."
            className="flex-1 bg-surface2 border border-border rounded-xl px-4 py-3 text-sm outline-none focus:border-violet/60"
          />
          <button
            onClick={send}
            disabled={loading}
            className="bg-violet hover:bg-violet/90 disabled:opacity-60 px-5 py-3 rounded-xl text-sm font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
