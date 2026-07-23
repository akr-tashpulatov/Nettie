"use client";

import { useState } from "react";
import toast from "react-hot-toast";

import { useExplainQuestionMutation } from "../api/exam-api";

/**
 * Fetches and caches AI explanations per question for the lifetime of the page,
 * so re-opening a question the student already asked about shows it instantly
 * without another request.
 */
export function useQuestionExplanation() {
  const mutation = useExplainQuestionMutation();
  const [explanations, setExplanations] = useState<Record<number, string>>({});
  const [loadingId, setLoadingId] = useState<number | null>(null);

  const explain = async (questionId: number) => {
    if (explanations[questionId] != null || loadingId != null) return;
    setLoadingId(questionId);
    try {
      const res = await mutation.mutateAsync({ questionId });
      setExplanations((prev) => ({ ...prev, [questionId]: res.explanation }));
    } catch {
      toast.error("Could not load the explanation");
    } finally {
      setLoadingId(null);
    }
  };

  return {
    explanationFor: (questionId: number): string | undefined => explanations[questionId],
    isExplaining: (questionId: number): boolean => loadingId === questionId,
    explain,
  };
}
