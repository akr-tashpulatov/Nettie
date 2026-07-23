import { notFound } from "next/navigation";

import { AdminTestDetailPage } from "@/features/admin-tests/ui/test-detail-page";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const testId = Number(id);
  if (!Number.isInteger(testId)) notFound();

  return <AdminTestDetailPage testId={testId} />;
}
