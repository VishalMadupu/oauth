import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function getSession() {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  if (!token) return null;
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/me`, {
      headers: { Cookie: `token=${token}` }
    });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}