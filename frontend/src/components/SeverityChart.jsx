import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { SEVERITIES, SEVERITY_COLORS } from "../constants";

export default function SeverityChart({ incidents }) {
  const data = SEVERITIES.map((severity) => ({
    severity,
    count: incidents.filter((incident) => incident.severity === severity).length,
  }));

  return (
    <div className="chart-card">
      <h3>Incidentes por severidade</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
          <XAxis dataKey="severity" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.severity} fill={SEVERITY_COLORS[entry.severity].fg} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
