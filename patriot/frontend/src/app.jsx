
import Layout from "../../../shared/ui/components/Layout/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
// import TokenHandler from "./components/TokenHandler.jsx";

// HUD Components
import HUDEffects from "../../../shared/ui/components/HUD/HUDEffects";
import HUDLayer from "../../../shared/ui/components/HUD/HUDLayer";

// Pages
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import Bills from "./pages/Bills/Bills.jsx";
import Funds from "./pages/Funds/Funds.jsx";
import Income from "./pages/Income/Income.jsx";
import Reports from "./pages/Reports/Reports.jsx";
import { Routes, Route, Navigate } from "react-router-dom";
import AuthCallback from "./pages/Auth/AuthCallback.jsx";
import Settings from "./pages/Settings/Settings.jsx";
import Accounts from "./pages/Accounts/Accounts.jsx";

export default function App() {
  return (
    <>
      {/* HUD Effects Layer (static, global) */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 4, pointerEvents: 'none' }}>
        <HUDEffects />
        <HUDLayer />
      </div>
      <Routes>
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route
          path="/accounts"
          element={
            <ProtectedRoute>
              <Layout>
                <Accounts />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/bills"
          element={
            <ProtectedRoute>
              <Layout>
                <Bills />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/funds"
          element={
            <ProtectedRoute>
              <Layout>
                <Funds />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/income"
          element={
            <ProtectedRoute>
              <Layout>
                <Income />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <Layout>
                <Reports />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </>
  );
}