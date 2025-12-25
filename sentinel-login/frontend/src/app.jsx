import React from "react";

import { Routes, Route, Navigate } from "react-router-dom";
import PatriotLogin from "./pages/Patriot-Login/Patriot-Login";
import Register from "./pages/Register/Register";

const App = () => {
    return (
        <Routes>
            <Route path="/login" element={<PatriotLogin />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    );
};

export default App;
