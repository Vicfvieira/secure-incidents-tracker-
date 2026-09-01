import { SEVERITIES, STATUSES } from "../constants";

export default function IncidentFilters({ severity, status, onChange }) {
  return (
    <div className="filters">
      <label>
        Severidade
        <select
          value={severity}
          onChange={(e) => onChange({ severity: e.target.value, status })}
        >
          <option value="">Todas</option>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>

      <label>
        Status
        <select
          value={status}
          onChange={(e) => onChange({ severity, status: e.target.value })}
        >
          <option value="">Todos</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
