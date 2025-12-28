
import { Routes, Route, Navigate } from "react-router-dom";



import HUDEffects from "shared/ui/components/HUD/HUDEffects";
import HUDLayer from "shared/ui/components/HUD/HUDLayer";
import PatriotLogin from "./pages/Patriot-Login/Patriot-Login";
import Register from "./pages/Register/Register";
import patriotTheme from "./pages/Patriot-Login/PatriotLoginTheme.module.css";
import registerTheme from "./pages/Register/Register.module.css";


const App = () => {
    return (
        <>
            {/* HUD Effects Layer (static, global) */}
            <div style={{ position: 'fixed', inset: 0, zIndex: 4, pointerEvents: 'none' }}>
                <HUDEffects />
                <HUDLayer />
            </div>
            <Routes>
                <Route path="/patriot-login" element={<div className={patriotTheme["page-theme-patriot"]}><PatriotLogin /></div>} />
                <Route path="/register" element={<div className={registerTheme["background"]}><Register /></div>} />
                <Route path="*" element={<Navigate to="/patriot-login" replace />} />
            </Routes>
        </>
    );
};

export default App;
