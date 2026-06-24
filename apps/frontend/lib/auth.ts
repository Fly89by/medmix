export interface User {
  id: number;
  email: string;
  name: string;
  role?: string;
}

export async function login(email: string, password: string): Promise<string> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(err.detail || 'Login failed');
  }
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data.access_token;
}

export async function getMe(): Promise<User> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Not authenticated');
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Session expired');
  return res.json();
}

export function logout() {
  localStorage.removeItem('token');
  if (typeof window !== 'undefined') window.location.href = '/login';
}
