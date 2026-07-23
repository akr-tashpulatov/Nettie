'use client';

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Check, Pencil, Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

import type { QuestionResponse } from "@/shared/api/generated/model";
import { ROUTES } from "@/shared/constants/routes";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { ConfirmDialog } from "@/shared/components/confirm-dialog";
import { cn } from "@/shared/lib/utils";
import {
  useTestQuery,
  useQuestionsQuery,
  useDeleteQuestionMutation,
} from "../api/tests-api";
import { ImportQuestionsButton } from "./import-questions-button";
import { QuestionFormDialog } from "./question-form-dialog";

export function AdminTestDetailPage({ testId }: { testId: number }) {
  const { data: test } = useTestQuery(testId);
  const { data: questions, isLoading } = useQuestionsQuery(testId);
  const deleteMutation = useDeleteQuestionMutation();

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<QuestionResponse | null>(null);
  const [deleting, setDeleting] = useState<QuestionResponse | null>(null);

  const openAdd = () => {
    setEditing(null);
    setFormOpen(true);
  };

  const openEdit = (q: QuestionResponse) => {
    setEditing(q);
    setFormOpen(true);
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    try {
      await deleteMutation.mutateAsync({ testId, questionId: deleting.id });
      toast.success("Question deleted");
      setDeleting(null);
    } catch {
      toast.error("Failed to delete question");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <Link
        href={ROUTES.ADMIN_TESTS}
        className="inline-flex w-fit items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" /> Back to tests
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{test?.name ?? "Test"}</h1>
          {test ? (
            <p className="mt-1 text-sm text-muted-foreground">
              {test.mode} questions per session · {test.question_count} question
              {test.question_count === 1 ? "" : "s"} in bank
            </p>
          ) : null}
        </div>
        <div className="flex gap-2">
          <ImportQuestionsButton testId={testId} />
          <Button onClick={openAdd}>
            <Plus className="size-4" /> Add question
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner className="size-6" />
        </div>
      ) : questions && questions.length > 0 ? (
        <ol className="flex flex-col gap-4">
          {questions.map((q, index) => (
            <li key={q.id} className="rounded-lg border bg-background p-4">
              <div className="flex items-start justify-between gap-4">
                <p className="font-medium">
                  <span className="text-muted-foreground">{index + 1}.</span>{" "}
                  {q.text}
                </p>
                <div className="flex shrink-0 gap-1">
                  <Button variant="ghost" size="icon-sm" onClick={() => openEdit(q)}>
                    <Pencil className="size-4" />
                  </Button>
                  <Button variant="ghost" size="icon-sm" onClick={() => setDeleting(q)}>
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </div>
              </div>
              <ul className="mt-3 flex flex-col gap-1.5">
                {q.options.map((o) => (
                  <li
                    key={o.id}
                    className={cn(
                      "flex items-center gap-2 rounded-md px-3 py-1.5 text-sm",
                      o.is_correct
                        ? "bg-emerald-50 text-emerald-700"
                        : "text-foreground",
                    )}
                  >
                    {o.is_correct ? (
                      <Check className="size-4 text-emerald-600" />
                    ) : (
                      <span className="size-4" />
                    )}
                    {o.text}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ol>
      ) : (
        <div className="rounded-lg border border-dashed bg-background p-10 text-center text-muted-foreground">
          No questions yet. Import a .docx file or add questions manually.
        </div>
      )}

      <QuestionFormDialog
        testId={testId}
        open={formOpen}
        onOpenChange={setFormOpen}
        question={editing}
      />

      <ConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => !open && setDeleting(null)}
        title="Delete question?"
        description="This question will be permanently removed from the test."
        isLoading={deleteMutation.isPending}
        onConfirm={confirmDelete}
      />
    </div>
  );
}
