
import { Routes, Route, Navigate } from "react-router-dom";

import ErrorBoundary from "shared/ui/components/ErrorBoundary/ErrorBoundary";
import AuthErrorBoundary from "shared/ui/components/ErrorBoundary/AuthErrorBoundary";
import { AuthProvider } from "./contexts/AuthContext";

import HUDEffects from "shared/ui/components/HUD/HUDEffects";
import HUDLayer from "shared/ui/components/HUD/HUDLayer";

import PatriotLogin from "./pages/Patriot-Login/Patriot-Login";
import Register from "./pages/Register/Register";
import PasswordReset from "./pages/PasswordReset/PasswordReset";
import patriotTheme from "./pages/Patriot-Login/PatriotLoginTheme.module.css";
import registerTheme from "./pages/Register/Register.module.css";
import { TransitionProvider, useTransitionOverlay } from "./TransitionOverlayContext.jsx";
import StarkPageTransition from "shared/ui/components/StarkPageTransition";
import { useLocation } from "react-router-dom";




// App-level transition overlay with destination background
function AppTransitionOverlay() {
    const { active, direction } = useTransitionOverlay();
    const location = useLocation();
    // Determine destination background class based on route
    let destBackgroundClass = "";
    if (location.pathname === "/register") {
        destBackgroundClass = ""; // Register background is handled by Register.module.css
    } else if (location.pathname === "/patriot-login") {
        destBackgroundClass = patriotTheme.background;
    }
    return (
        <StarkPageTransition
            active={active}
            direction={direction}
            destBackgroundClass={destBackgroundClass}
        />
    );
}

const App = () => {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <TransitionProvider>
                    {/* HUD Effects Layer (static, global) */}
                    <div style={{ position: 'fixed', inset: 0, zIndex: 1, pointerEvents: 'none' }}>
                        <HUDEffects />
                        <HUDLayer />
                    </div>
                    <AppTransitionOverlay />
                    <AuthErrorBoundary>
                        <Routes>
                            <Route path="/patriot-login" element={<div className={patriotTheme["page-theme-patriot"]}><PatriotLogin /></div>} />
                            <Route path="/register" element={<div className={registerTheme["background"]}><Register /></div>} />
                            <Route path="/reset-password" element={<PasswordReset />} />
                            <Route path="*" element={<Navigate to="/patriot-login" replace />} />
                        </Routes>
                    </AuthErrorBoundary>
                </TransitionProvider>
            </AuthProvider>
        </ErrorBoundary>
    );
};

export default App;
