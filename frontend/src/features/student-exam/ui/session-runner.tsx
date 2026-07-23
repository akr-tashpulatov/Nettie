'use client';

import Link from "next/link";
import { Check, ChevronLeft, ChevronRight, Sparkles, X } from "lucide-react";

import type { SessionResponse, SessionOptionView } from "@/shared/api/generated/model";
import { ROUTES } from "@/shared/constants/routes";
import { Button } from "@/shared/components/ui/button";
import { MathText } from "@/shared/components/math-text";
import { cn } from "@/shared/lib/utils";
import { useTakeSession, type QuestionResult } from "../model/use-take-session";
import { useQuestionExplanation } from "../model/use-question-explanation";

type OptionState = "correct" | "wrong" | "selected" | "idle";

function optionState(
  option: SessionOptionView,
  result: QuestionResult | undefined,
  selected: number | null,
): OptionState {
  if (result) {
    if (option.id === result.correctOptionId) return "correct";
    if (option.id === result.selectedOptionId) {
      return result.isCorrect ? "correct" : "wrong";
    }
    return "idle";
  }
  return option.id === selected ? "selected" : "idle";
}

const optionClasses: Record<OptionState, string> = {
  correct: "border-emerald-500 bg-emerald-50 text-emerald-800",
  wrong: "border-red-500 bg-red-50 text-red-800",
  selected: "border-primary bg-primary/5",
  idle: "border-border hover:bg-accent",
};

export function SessionRunner({ session }: { session: SessionResponse }) {
  const s = useTakeSession(session);
  const explanation = useQuestionExplanation();
  const { currentItem, currentResult } = s;

  if (!currentItem) {
    return <p className="text-muted-foreground">This session has no questions.</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Progress header */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Question {s.current + 1} of {s.total}
          </span>
          <span>
            Score: {s.correctCount} / {s.answeredCount}
          </span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${(s.answeredCount / s.total) * 100}%` }}
          />
        </div>
      </div>

      {s.isComplete ? (
        <div className="flex flex-col items-center gap-3 rounded-lg border bg-background p-6 text-center">
          <p className="text-lg font-semibold">Session complete!</p>
          <p className="text-3xl font-bold">
            {s.correctCount}
            <span className="text-muted-foreground">/{s.total}</span>
          </p>
          <p className="text-sm text-muted-foreground">
            {Math.round((s.correctCount / s.total) * 100)}% correct
          </p>
          <div className="mt-2 flex gap-2">
            <Button asChild variant="outline">
              <Link href={ROUTES.STUDENT_TESTS}>Take another test</Link>
            </Button>
            <Button asChild>
              <Link href={ROUTES.STUDENT_SESSIONS}>My results</Link>
            </Button>
          </div>
        </div>
      ) : null}

      {/* Question card */}
      <div className="rounded-lg border bg-background p-6">
        <p className="text-lg font-medium">
          <MathText>{currentItem.text}</MathText>
        </p>

        <div className="mt-5 flex flex-col gap-2.5">
          {currentItem.options.map((option) => {
            const state = optionState(option, currentResult, s.selected);
            const locked = !!currentResult;
            return (
              <button
                key={option.id}
                type="button"
                disabled={locked}
                onClick={() => s.setSelected(option.id)}
                className={cn(
                  "flex items-center justify-between gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                  optionClasses[state],
                  locked ? "cursor-default" : "cursor-pointer",
                )}
              >
                <MathText>{option.text}</MathText>
                {state === "correct" ? (
                  <Check className="size-4 shrink-0 text-emerald-600" />
                ) : state === "wrong" ? (
                  <X className="size-4 shrink-0 text-red-600" />
                ) : null}
              </button>
            );
          })}
        </div>

        {currentResult ? (
          <p
            className={cn(
              "mt-4 text-sm font-medium",
              currentResult.isCorrect ? "text-emerald-700" : "text-red-700",
            )}
          >
            {currentResult.isCorrect
              ? "Correct!"
              : "Incorrect — the correct answer is highlighted above."}
          </p>
        ) : null}

        {currentResult ? (
          <div className="mt-4">
            {explanation.explanationFor(currentItem.question_id) ? (
              <div className="rounded-lg border bg-muted/40 p-4">
                <p className="mb-1.5 flex items-center gap-1.5 text-sm font-medium text-primary">
                  <Sparkles className="size-4" /> AI explanation
                </p>
                <div className="text-sm leading-relaxed text-foreground">
                  <MathText>
                    {explanation.explanationFor(currentItem.question_id)!}
                  </MathText>
                </div>
              </div>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={() => explanation.explain(currentItem.question_id)}
                isLoading={explanation.isExplaining(currentItem.question_id)}
              >
                <Sparkles className="size-4" /> Explain with AI
              </Button>
            )}
          </div>
        ) : null}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={s.prev}
          disabled={s.current === 0}
        >
          <ChevronLeft className="size-4" /> Previous
        </Button>

        {currentResult ? (
          <Button onClick={s.next} disabled={s.isLastQuestion}>
            Next <ChevronRight className="size-4" />
          </Button>
        ) : (
          <Button
            onClick={s.submitAnswer}
            disabled={s.selected == null}
            isLoading={s.isSubmitting}
          >
            OK
          </Button>
        )}
      </div>
    </div>
  );
}
