import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import TextBox from "shared/ui/components/TextBox/TextBox";
import Button from "shared/ui/components/Button/Button";

const PasswordReset = () => {
    const [identifier, setIdentifier] = useState("");
    const [securityQuestion, setSecurityQuestion] = useState("");
    const [securityAnswer, setSecurityAnswer] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [step, setStep] = useState(1);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    const handleRequest = async e => {
        e.preventDefault();
        setError("");
        setSuccess("");
        try {
            const res = await fetch("/auth/password-reset/request", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: identifier, username: identifier })
            });
            const data = await res.json();
            if (res.ok && data.security_question) {
                setSecurityQuestion(data.security_question);
                setStep(2);
            } else {
                setError(data.error || "User not found or no security question set.");
            }
        } catch {
            setError("Network error. Try again.");
        }
    };

    const handleReset = async e => {
        e.preventDefault();
        setError("");
        setSuccess("");
        try {
            const res = await fetch("/auth/password-reset/confirm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: identifier, username: identifier, security_answer: securityAnswer, new_password: newPassword })
            });
            const data = await res.json();
            if (res.ok) {
                setSuccess("Password reset successful! You may now log in.");
                setTimeout(() => navigate("/patriot-login"), 2000);
            } else {
                setError(data.error || "Password reset failed.");
            }
        } catch {
            setError("Network error. Try again.");
        }
    };

    return (
        <div style={{ maxWidth: 400, margin: "40px auto", padding: 24, background: "#181c24", borderRadius: 12, boxShadow: "0 2px 16px #0006" }}>
            <h2 style={{ textAlign: "center", marginBottom: 24 }}>Reset Password</h2>
            {step === 1 && (
                <form onSubmit={handleRequest}>
                    <TextBox
                        id="reset-identifier"
                        value={identifier}
                        onChange={setIdentifier}
                        placeholder="Email or Username"
                        type="text"
                        required
                        style={{ marginBottom: 16 }}
                    />
                    <Button type="submit">Next</Button>
                </form>
            )}
            {step === 2 && (
                <form onSubmit={handleReset}>
                    <div style={{ marginBottom: 16, fontWeight: 600 }}>{securityQuestion}</div>
                    <TextBox
                        id="reset-security-answer"
                        value={securityAnswer}
                        onChange={setSecurityAnswer}
                        placeholder="Security Answer"
                        type="text"
                        required
                        style={{ marginBottom: 16 }}
                    />
                    <TextBox
                        id="reset-new-password"
                        value={newPassword}
                        onChange={setNewPassword}
                        placeholder="New Password"
                        type="password"
                        required
                        style={{ marginBottom: 16 }}
                    />
                    <Button type="submit">Reset Password</Button>
                </form>
            )}
            {error && <div style={{ color: "#ef4444", marginTop: 16, fontWeight: 600 }}>{error}</div>}
            {success && <div style={{ color: "#21c55d", marginTop: 16, fontWeight: 600 }}>{success}</div>}
        </div>
    );
};

export default PasswordReset;
