'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

import { SessionStatus } from "@/shared/api/generated/model";
import { ROUTES } from "@/shared/constants/routes";
import { Button } from "@/shared/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { Spinner } from "@/shared/components/ui/spinner";
import { TablePagination } from "@/shared/components/pagination";
import { cn } from "@/shared/lib/utils";
import { useSessionsQuery } from "../api/exam-api";

export function StudentHistoryPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useSessionsQuery({ page, limit: 10 });

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold">My results</h1>

      <div className="rounded-lg border bg-background">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead className="w-32">Status</TableHead>
              <TableHead className="w-28">Score</TableHead>
              <TableHead className="w-28 text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="h-32 text-center">
                  <Spinner className="mx-auto size-6" />
                </TableCell>
              </TableRow>
            ) : data && data.items.length > 0 ? (
              data.items.map((session) => {
                const completed = session.status === SessionStatus.COMPLETED;
                return (
                  <TableRow key={session.id}>
                    <TableCell>
                      {format(new Date(session.created_at), "dd MMM yyyy, HH:mm")}
                    </TableCell>
                    <TableCell>
                      <span
                        className={cn(
                          "rounded-full px-2 py-0.5 text-xs font-medium",
                          completed
                            ? "bg-emerald-50 text-emerald-700"
                            : "bg-amber-50 text-amber-700",
                        )}
                      >
                        {completed ? "Completed" : "In progress"}
                      </span>
                    </TableCell>
                    <TableCell>
                      {session.correct_count} / {session.total}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          router.push(ROUTES.STUDENT_SESSION(session.id))
                        }
                      >
                        {completed ? "Review" : "Resume"}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="h-32 text-center text-muted-foreground"
                >
                  You haven&apos;t taken any tests yet.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {data && data.page_count > 1 ? (
        <TablePagination
          page={page}
          pageCount={data.page_count}
          onPageChange={setPage}
        />
      ) : null}
    </div>
  );
}
