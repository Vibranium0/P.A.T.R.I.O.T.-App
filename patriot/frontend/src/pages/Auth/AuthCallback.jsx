import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

// Utility to parse query params
function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}

export default function AuthCallback() {
    const navigate = useNavigate();

    useEffect(() => {
        const token = getQueryParam("token");
        if (token) {
            // Store token in localStorage
            localStorage.setItem("sentinel_token", token);
            // Clean URL (remove token)
            window.history.replaceState({}, document.title, window.location.pathname);
            // Redirect to dashboard
            navigate("/dashboard", { replace: true });
        } else {
            // No token, redirect to login or home
            navigate("/", { replace: true });
        }
    }, [navigate]);

    return null; // Optionally, show a loading spinner
}
