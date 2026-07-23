import { notFound } from "next/navigation";

import { SessionPage } from "@/features/student-exam/ui/session-page";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const sessionId = Number(id);
  if (!Number.isInteger(sessionId)) notFound();

  return <SessionPage sessionId={sessionId} />;
}
