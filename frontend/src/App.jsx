import React, { useEffect, useState } from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Landing from "./pages/Landing.jsx";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Chat from "./pages/Chat.jsx";
import MemoryTimeline from "./pages/MemoryTimeline.jsx";
import Settings from "./pages/Settings.jsx";
import Profile from "./pages/Profile.jsx";
import Analytics from "./pages/Analytics.jsx";

const STORAGE_KEY = "persona_twin_user";

export default function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) setUser(JSON.parse(stored));
    setReady(true);
  }, []);

  function handleLogin(u) {
    setUser(u);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
  }

  function handleLogout() {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  if (!ready) return null;

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} />

      {user ? (
        <Route element={<AppShell user={user} onLogout={handleLogout} />}>
          <Route path="/dashboard" element={<Dashboard user={user} />} />
          <Route path="/chat" element={<Chat user={user} />} />
          <Route path="/memory" element={<MemoryTimeline user={user} />} />
          <Route path="/settings" element={<Settings user={user} />} />
          <Route path="/profile" element={<Profile user={user} />} />
          <Route path="/analytics" element={<Analytics user={user} />} />
        </Route>
      ) : (
        <Route path="*" element={<Navigate to="/login" />} />
      )}

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function AppShell({ user, onLogout }) {
  return (
    <div className="flex">
      <Sidebar user={user} onLogout={onLogout} />
      <main className="flex-1 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}
