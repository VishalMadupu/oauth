import Image from "next/image";

export default function Home() {
  const api = process.env.NEXT_PUBLIC_API_URL;
  return (
    <main className="p-8 flex flex-col gap-4 items-center">
      <h1 className="text-3xl font-bold">OAuth Login Demo</h1>
      <div className="flex gap-4">
        <a href={`${api}/auth/google`} className="bg-blue-600 text-white px-6 py-2 rounded">🔵 Google</a>
        <a href={`${api}/auth/github`} className="bg-gray-800 text-white px-6 py-2 rounded">⚫ GitHub</a>
      </div>
      <a href="/dashboard" className="text-blue-500 underline">Go to Dashboard</a>
    </main>
  );
}