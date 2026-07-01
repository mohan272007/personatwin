import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/api.js";

export default function Login({ onLogin }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setError("");
    try {
      const user = await api.mockLogin(email, name || "Demo User");
      onLogin(user);
      navigate("/dashboard");
    } catch (err) {
      setError("Could not reach the backend. Is it running on :8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 mb-8 justify-center">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet to-cyan flex items-center justify-center font-display font-bold">P</div>
          <span className="font-display font-semibold text-lg">PersonaTwin AI</span>
        </div>

        <div className="glass rounded-2xl p-7">
          <h1 className="font-display text-xl mb-1">Welcome back</h1>
          <p className="text-sm text-muted mb-6">Sign in to load your digital twin.</p>

          <form onSubmit={handleLogin} className="space-y-3">
            <div>
              <label className="text-xs text-muted block mb-1">Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ada Lovelace"
                className="w-full bg-surface2 border border-border rounded-lg px-3 py-2.5 text-sm outline-none focus:border-violet/60"
              />
            </div>
            <div>
              <label className="text-xs text-muted block mb-1">Email</label>
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ada@example.com"
                className="w-full bg-surface2 border border-border rounded-lg px-3 py-2.5 text-sm outline-none focus:border-violet/60"
              />
            </div>

            {error && <p className="text-xs text-red-400">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-violet hover:bg-violet/90 disabled:opacity-60 rounded-lg py-2.5 text-sm font-medium transition-colors"
            >
              {loading ? "Signing in..." : "Continue with Google"}
            </button>
          </form>

          <p className="text-[11px] text-muted mt-5 leading-relaxed">
            Demo mode: this simulates Google OAuth so judges can sign in instantly
            without setting up OAuth credentials. Real Google OAuth can be dropped in
            behind the same <code className="text-cyan">/auth/google</code> endpoint.
          </p>
        </div>
      </div>
    </div>
  );
}
