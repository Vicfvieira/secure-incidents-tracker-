import { useState } from "react";
import { createIncident } from "../api/incidents";
import { extractErrorMessage } from "../api/client";
import { INCIDENT_TYPES, SEVERITIES } from "../constants";

const EMPTY_FORM = {
  title: "",
  description: "",
  severity: "MEDIUM",
  type: INCIDENT_TYPES[0],
  indicators: "",
};

export default function IncidentForm({ onCreated }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const payload = {
        title: form.title,
        description: form.description,
        severity: form.severity,
        type: form.type,
        indicators: form.indicators
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      };
      const created = await createIncident(payload);
      setForm(EMPTY_FORM);
      onCreated?.(created);
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível criar o incidente."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="incident-form" onSubmit={handleSubmit}>
      <h3>Reportar novo incidente</h3>

      <label>
        Título
        <input
          type="text"
          required
          value={form.title}
          onChange={(e) => update("title", e.target.value)}
          placeholder="Suspeita de Phishing no RH"
        />
      </label>

      <label>
        Descrição
        <textarea
          required
          rows={3}
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
          placeholder="Descreva o que aconteceu..."
        />
      </label>

      <div className="form-row">
        <label>
          Severidade
          <select value={form.severity} onChange={(e) => update("severity", e.target.value)}>
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label>
          Tipo
          <select value={form.type} onChange={(e) => update("type", e.target.value)}>
            {INCIDENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label>
        Indicadores de comprometimento (separados por vírgula)
        <input
          type="text"
          value={form.indicators}
          onChange={(e) => update("indicators", e.target.value)}
          placeholder="malicious-link.com, 192.168.1.50"
        />
      </label>

      {error && <p className="error-message">{error}</p>}

      <button type="submit" disabled={submitting}>
        {submitting ? "Enviando..." : "Criar incidente"}
      </button>
    </form>
  );
}
