
import Layout from "../../../shared/ui/components/Layout/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import TokenHandler from "./components/TokenHandler.jsx";

// Pages
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import PatriotLogin from "../../sentinel_login/frontend/src/pages/Patriot-Login/Patriot-Login.jsx";
import Bills from "./pages/Bills/Bills.jsx";
import Funds from "./pages/Funds/Funds.jsx";
import Income from "./pages/Income/Income.jsx";
import Reports from "./pages/Reports/Reports.jsx";
import { Routes, Route, Navigate } from "react-router-dom";
import Settings from "./pages/Settings/Settings.jsx";
import Accounts from "./pages/Accounts/Accounts.jsx";

export default function App() {
  return (
    <TokenHandler>
      <Routes>
        <Route
          path="/login"
          element={<PatriotLogin />}
        />
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
    </TokenHandler>
  );
}