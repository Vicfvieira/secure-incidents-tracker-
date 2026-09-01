import { apiClient } from "./client";

export function login(email, password) {
  return apiClient.post("/auth/login", { email, password }).then((res) => res.data);
}

export function register(email, password, fullName) {
  return apiClient
    .post("/auth/register", { email, password, full_name: fullName })
    .then((res) => res.data);
}

export function getCurrentUser() {
  return apiClient.get("/users/me").then((res) => res.data);
}
