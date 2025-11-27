
import Layout from "./components/Layout/Layout.jsx";


// Pages
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import Login from "./pages/Login/Login.jsx";
import Bills from "./pages/Bills/Bills.jsx";
import Funds from "./pages/Funds/Funds.jsx";
import Income from "./pages/Income/Income.jsx";
import Reports from "./pages/Reports/Reports.jsx";
import { Routes, Route, Navigate } from "react-router-dom";
import Settings from "./pages/Settings/Settings.jsx";
import Accounts from "./pages/Accounts/Accounts.jsx";

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<Login />}
      />
      <Route
        path="/accounts"
        element={
          <Layout>
            <Accounts />
          </Layout>
        }
      />
      <Route
        path="/"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />
      <Route
        path="/dashboard"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />
      <Route
        path="/bills"
        element={
          <Layout>
            <Bills />
          </Layout>
        }
      />
      <Route
        path="/funds"
        element={
          <Layout>
            <Funds />
          </Layout>
        }
      />
      <Route
        path="/income"
        element={
          <Layout>
            <Income />
          </Layout>
        }
      />
      <Route
        path="/reports"
        element={
          <Layout>
            <Reports />
          </Layout>
        }
      />
      <Route
        path="/settings"
        element={
          <Layout>
            <Settings />
          </Layout>
        }
      />
      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}