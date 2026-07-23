'use client';

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { ROUTES } from "@/shared/constants/routes";
import { Spinner } from "@/shared/components/ui/spinner";
import { useSessionQuery } from "../api/exam-api";
import { SessionRunner } from "./session-runner";

export function SessionPage({ sessionId }: { sessionId: number }) {
  const { data, isLoading, isError } = useSessionQuery(sessionId);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <Link
        href={ROUTES.STUDENT_TESTS}
        className="inline-flex w-fit items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" /> Exit
      </Link>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner className="size-6" />
        </div>
      ) : isError || !data ? (
        <p className="text-muted-foreground">
          This session could not be loaded. It may not exist or belong to you.
        </p>
      ) : (
        <SessionRunner session={data} />
      )}
    </div>
  );
}
