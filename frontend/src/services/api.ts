const API_BASE_URL = "http://127.0.0.1:8000";

export type AuthToken = {
  access_token: string;
  token_type: string;
};

export type RegisterData = {
  email: string;
  password: string;
};

export type CurrentUser = {
  id: string;
  email: string;
  is_active: boolean;
};

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  // Attach the access token without storing or logging passwords.
  const token = sessionStorage.getItem("access_token");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
        ? data.detail
        : `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data as T;
}

export async function registerUser(data: RegisterData): Promise<CurrentUser> {
  return apiRequest<CurrentUser>("/api/v1/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function loginUser(
  email: string,
  password: string,
): Promise<AuthToken> {
  return apiRequest<AuthToken>("/api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email.trim(),
      password,
    }),
  });
}

export async function getCurrentUser(): Promise<CurrentUser> {
  return apiRequest<CurrentUser>("/api/v1/auth/me");
}

export function logoutUser(): void {
  sessionStorage.removeItem("access_token");
}
