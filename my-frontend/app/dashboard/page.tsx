import { getSession } from "@/app/lib/auth";
import { redirect } from "next/navigation";

export default async function Dashboard() {
  const user = await getSession();
  if (!user) redirect("/");

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold">🔒 Dashboard</h1>
      <p>Welcome, {user.email}</p>
      <a href={`${process.env.NEXT_PUBLIC_API_URL}/logout`} className="text-red-500 underline mt-4 block">Logout</a>
    </main>
  );
}