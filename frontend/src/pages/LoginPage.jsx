import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register as registerRequest } from "../api/auth";
import { extractErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "register") {
        await registerRequest(email, password, fullName);
      }
      await login(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível entrar."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>🛡️ Secure Incidents Tracker</h1>
        <p className="login-subtitle">
          {mode === "login" ? "Entre com sua conta" : "Crie sua conta"}
        </p>

        {mode === "register" && (
          <label>
            Nome completo
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </label>
        )}

        <label>
          E-mail
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
          />
        </label>

        <label>
          Senha
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta e entrar"}
        </button>

        <button
          type="button"
          className="btn-link"
          onClick={() => {
            setError("");
            setMode(mode === "login" ? "register" : "login");
          }}
        >
          {mode === "login" ? "Não tem conta? Criar uma agora" : "Já tem conta? Entrar"}
        </button>
      </form>
    </div>
  );
}
