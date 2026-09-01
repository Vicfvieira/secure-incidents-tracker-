import { SEVERITY_COLORS } from "../constants";

export default function SeverityBadge({ severity }) {
  const colors = SEVERITY_COLORS[severity] || { bg: "#eee", fg: "#333", border: "#ccc" };
  return (
    <span
      className="severity-badge"
      style={{ backgroundColor: colors.bg, color: colors.fg, borderColor: colors.border }}
    >
      {severity}
    </span>
  );
}
