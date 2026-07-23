'use client';

import { useEffect } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { Plus, Trash2 } from "lucide-react";

import type { QuestionResponse } from "@/shared/api/generated/model";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { cn } from "@/shared/lib/utils";
import { questionFormSchema, type QuestionFormData } from "../model/schemas";
import {
  useAddQuestionMutation,
  useUpdateQuestionMutation,
} from "../api/tests-api";

interface Props {
  testId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  question?: QuestionResponse | null;
}

const emptyDefaults: QuestionFormData = {
  text: "",
  correctIndex: 0,
  options: [{ text: "" }, { text: "" }],
};

export function QuestionFormDialog({ testId, open, onOpenChange, question }: Props) {
  const isEdit = !!question;
  const addMutation = useAddQuestionMutation();
  const updateMutation = useUpdateQuestionMutation();

  const {
    register,
    handleSubmit,
    control,
    reset,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<QuestionFormData>({
    resolver: zodResolver(questionFormSchema),
    defaultValues: emptyDefaults,
  });

  const { fields, append, remove } = useFieldArray({ control, name: "options" });
  const correctIndex = watch("correctIndex");

  useEffect(() => {
    if (!open) return;
    if (question) {
      const idx = Math.max(
        0,
        question.options.findIndex((o) => o.is_correct),
      );
      reset({
        text: question.text,
        correctIndex: idx,
        options: question.options.map((o) => ({ text: o.text })),
      });
    } else {
      reset(emptyDefaults);
    }
  }, [open, question, reset]);

  const onSubmit = async (data: QuestionFormData) => {
    const payload = {
      text: data.text,
      options: data.options.map((o, i) => ({
        text: o.text,
        is_correct: i === data.correctIndex,
      })),
    };
    try {
      if (isEdit && question) {
        await updateMutation.mutateAsync({
          testId,
          questionId: question.id,
          data: payload,
        });
        toast.success("Question updated");
      } else {
        await addMutation.mutateAsync({ testId, data: payload });
        toast.success("Question added");
      }
      onOpenChange(false);
    } catch {
      toast.error("Something went wrong");
    }
  };

  const removeOption = (index: number) => {
    remove(index);
    if (correctIndex === index) {
      setValue("correctIndex", 0);
    } else if (correctIndex > index) {
      setValue("correctIndex", correctIndex - 1);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit question" : "Add question"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="q-text">Question</Label>
            <Input id="q-text" placeholder="Question text" {...register("text")} />
            {errors.text ? (
              <p className="text-xs text-destructive">{errors.text.message}</p>
            ) : null}
          </div>

          <div className="flex flex-col gap-2">
            <Label>Options — select the correct one</Label>
            {fields.map((field, index) => (
              <div key={field.id} className="flex items-center gap-2">
                <input
                  type="radio"
                  className="size-4 accent-primary"
                  checked={correctIndex === index}
                  onChange={() => setValue("correctIndex", index)}
                  aria-label={`Mark option ${index + 1} correct`}
                />
                <Input
                  className={cn(correctIndex === index && "border-primary")}
                  placeholder={`Option ${index + 1}`}
                  {...register(`options.${index}.text`)}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-sm"
                  disabled={fields.length <= 2}
                  onClick={() => removeOption(index)}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
            ))}
            {errors.options ? (
              <p className="text-xs text-destructive">
                {errors.options.message ?? "Every option needs text"}
              </p>
            ) : null}
            {errors.correctIndex ? (
              <p className="text-xs text-destructive">{errors.correctIndex.message}</p>
            ) : null}
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="self-start"
              onClick={() => append({ text: "" })}
            >
              <Plus className="size-4" /> Add option
            </Button>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              {isEdit ? "Save" : "Add"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
