'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play } from "lucide-react";
import toast from "react-hot-toast";

import type { StudentTestResponse } from "@/shared/api/generated/model";
import { ROUTES } from "@/shared/constants/routes";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { TablePagination } from "@/shared/components/pagination";
import { useAvailableTestsQuery, useStartSessionMutation } from "../api/exam-api";

export function StudentTestsPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAvailableTestsQuery({ page, limit: 12 });
  const startMutation = useStartSessionMutation();
  const [startingId, setStartingId] = useState<number | null>(null);

  const start = async (test: StudentTestResponse) => {
    setStartingId(test.id);
    try {
      const session = await startMutation.mutateAsync({ testId: test.id });
      router.push(ROUTES.STUDENT_SESSION(session.id));
    } catch {
      toast.error("Could not start the session");
      setStartingId(null);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold">Take a test</h1>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner className="size-6" />
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            {data.items.map((test) => (
              <Card key={test.id}>
                <CardHeader>
                  <CardTitle>{test.name}</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    {test.mode} questions · random each attempt
                  </p>
                  <Button
                    onClick={() => start(test)}
                    isLoading={startMutation.isPending && startingId === test.id}
                    disabled={startMutation.isPending}
                  >
                    <Play className="size-4" /> Start
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {data.page_count > 1 ? (
            <TablePagination
              page={page}
              pageCount={data.page_count}
              onPageChange={setPage}
            />
          ) : null}
        </>
      ) : (
        <div className="rounded-lg border border-dashed bg-background p-10 text-center text-muted-foreground">
          No tests are available yet. Check back later.
        </div>
      )}
    </div>
  );
}
