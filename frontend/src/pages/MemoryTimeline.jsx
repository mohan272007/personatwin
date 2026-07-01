import React, { useEffect, useState } from "react";
import { api } from "../api/api.js";
import MemoryCard from "../components/MemoryCard.jsx";

export default function MemoryTimeline({ user }) {
  const [memories, setMemories] = useState([]);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.memoryTimeline(user.user_id, 200).then((m) => {
      setMemories(m);
      setLoading(false);
    });
  }, [user.user_id]);

  async function runSearch(e) {
    e.preventDefault();
    if (!query.trim()) {
      setSearchResults(null);
      return;
    }
    const results = await api.searchMemory(user.user_id, query, 8);
    setSearchResults(results);
  }

  const shown = searchResults ?? memories;
  const filtered = filter === "all" ? shown : shown.filter((m) => m.memory_type === filter);
  const types = ["all", ...new Set(memories.map((m) => m.memory_type))];

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="font-display text-2xl">Memory Timeline</h1>
        <p className="text-muted text-sm mt-1">
          Every memory is embedded and stored in Qdrant for semantic recall.
        </p>
      </div>

      <form onSubmit={runSearch} className="flex gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Semantic search -- try 'what do I like for breakfast'"
          className="flex-1 bg-surface2 border border-border rounded-xl px-4 py-2.5 text-sm outline-none focus:border-violet/60"
        />
        <button className="bg-violet hover:bg-violet/90 px-5 py-2.5 rounded-xl text-sm font-medium transition-colors">
          Search
        </button>
        {searchResults && (
          <button
            type="button"
            onClick={() => { setSearchResults(null); setQuery(""); }}
            className="px-4 py-2.5 rounded-xl text-sm border border-border text-muted"
          >
            Clear
          </button>
        )}
      </form>

      <div className="flex gap-2 flex-wrap">
        {types.map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              filter === t ? "border-violet/50 bg-violet/15 text-violet" : "border-border text-muted"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-muted">Loading memories...</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-muted glass rounded-xl p-6">
          Nothing here yet. Chat with your twin or upload something in Settings.
        </p>
      ) : (
        <div className="grid md:grid-cols-2 gap-3">
          {filtered.map((m) => (
            <MemoryCard key={m.id} {...m} />
          ))}
        </div>
      )}
    </div>
  );
}
