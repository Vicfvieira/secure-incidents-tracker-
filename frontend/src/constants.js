export const SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export const STATUSES = ["OPEN", "INVESTIGATING", "MITIGATED", "RESOLVED", "CLOSED"];

export const INCIDENT_TYPES = [
  "PHISHING",
  "DATA_LEAK",
  "MALWARE",
  "UNAUTHORIZED_ACCESS",
  "DENIAL_OF_SERVICE",
  "OTHER",
];

export const SEVERITY_COLORS = {
  LOW: { bg: "#e3f2e6", fg: "#1e7d32", border: "#8fd19e" },
  MEDIUM: { bg: "#fff6e0", fg: "#8a6100", border: "#f2c14e" },
  HIGH: { bg: "#ffe9dc", fg: "#b3400e", border: "#f2915a" },
  CRITICAL: { bg: "#fbe2e3", fg: "#a3182a", border: "#e37e88" },
};
