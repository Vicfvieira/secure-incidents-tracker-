import { apiClient } from "./client";

export function listIncidents({ page = 1, limit = 20, severity, status } = {}) {
  const params = { page, limit };
  if (severity) params.severity = severity;
  if (status) params.status = status;
  return apiClient.get("/incidents", { params }).then((res) => res.data);
}

export function createIncident(payload) {
  return apiClient.post("/incidents", payload).then((res) => res.data);
}
