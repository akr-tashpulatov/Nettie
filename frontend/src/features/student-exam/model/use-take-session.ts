'use client';

import { useMemo, useState } from "react";
import toast from "react-hot-toast";

import type { SessionResponse } from "@/shared/api/generated/model";
import { useAnswerQuestionMutation } from "../api/exam-api";

/**
 * Per-question outcome. `correctOptionId` is only known for questions answered
 * during this session run — the resume payload does not expose it for questions
 * that were already answered before the page loaded.
 */
export interface QuestionResult {
  selectedOptionId: number;
  isCorrect: boolean;
  correctOptionId?: number;
}

export function useTakeSession(session: SessionResponse) {
  const answerMutation = useAnswerQuestionMutation();

  const initialResults = useMemo(() => {
    const map: Record<number, QuestionResult> = {};
    for (const item of session.items) {
      if (item.answered && item.selected_option_id != null) {
        map[item.question_id] = {
          selectedOptionId: item.selected_option_id,
          isCorrect: !!item.is_correct,
        };
      }
    }
    return map;
  }, [session.items]);

  const firstUnanswered = useMemo(() => {
    const idx = session.items.findIndex((i) => !i.answered);
    return idx === -1 ? Math.max(0, session.items.length - 1) : idx;
  }, [session.items]);

  const [results, setResults] = useState<Record<number, QuestionResult>>(
    initialResults,
  );
  const [current, setCurrent] = useState(firstUnanswered);
  // Pending selection for the current (not yet submitted) question.
  const [selected, setSelected] = useState<number | null>(null);

  const items = session.items;
  const total = session.total;
  const answeredCount = Object.keys(results).length;
  const correctCount = Object.values(results).filter((r) => r.isCorrect).length;
  const isComplete = answeredCount >= total;

  const currentItem = items[current];
  const currentResult = currentItem ? results[currentItem.question_id] : undefined;

  const submitAnswer = async () => {
    if (!currentItem || selected == null || currentResult) return;
    try {
      const feedback = await answerMutation.mutateAsync({
        sessionId: session.id,
        data: {
          question_id: currentItem.question_id,
          selected_option_id: selected,
        },
      });
      setResults((prev) => ({
        ...prev,
        [currentItem.question_id]: {
          selectedOptionId: feedback.selected_option_id,
          isCorrect: feedback.is_correct,
          correctOptionId: feedback.correct_option_id,
        },
      }));
      setSelected(null);
    } catch {
      toast.error("Could not submit your answer");
    }
  };

  const goTo = (index: number) => {
    if (index < 0 || index >= items.length) return;
    setSelected(null);
    setCurrent(index);
  };

  const next = () => goTo(current + 1);
  const prev = () => goTo(current - 1);

  return {
    items,
    total,
    current,
    currentItem,
    currentResult,
    results,
    selected,
    setSelected,
    submitAnswer,
    isSubmitting: answerMutation.isPending,
    next,
    prev,
    goTo,
    answeredCount,
    correctCount,
    isComplete,
    isLastQuestion: current === items.length - 1,
  };
}
