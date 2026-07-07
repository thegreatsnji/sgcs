import { api } from "@/services/api/client";
import type { LoginCredentials, LoginResponse, RegisterData, User } from "@/types/auth";

export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/auth/login/", credentials);
  return data;
}

export async function register(userData: RegisterData): Promise<User> {
  const { data } = await api.post<User>("/auth/register/", userData);
  return data;
}

export async function logout(refresh: string): Promise<void> {
  await api.post("/auth/logout/", { refresh });
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/auth/me/");
  return data;
}
