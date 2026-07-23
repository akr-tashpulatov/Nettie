'use client';

import { useEffect } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { isAxiosError } from "axios";
import toast from "react-hot-toast";

import { TestMode } from "@/shared/api/generated/model";
import type { TestResponse } from "@/shared/api/generated/model";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { testFormSchema, type TestFormData } from "../model/schemas";
import {
  useCreateTestMutation,
  useUpdateTestMutation,
} from "../api/tests-api";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  test?: TestResponse | null;
}

export function TestFormDialog({ open, onOpenChange, test }: Props) {
  const isEdit = !!test;
  const createMutation = useCreateTestMutation();
  const updateMutation = useUpdateTestMutation();

  const {
    register,
    handleSubmit,
    control,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<TestFormData>({
    resolver: zodResolver(testFormSchema),
    defaultValues: { name: "", mode: TestMode.NUMBER_30 },
  });

  useEffect(() => {
    if (open) {
      reset({
        name: test?.name ?? "",
        mode: test?.mode ?? TestMode.NUMBER_30,
      });
    }
  }, [open, test, reset]);

  const onSubmit = async (data: TestFormData) => {
    try {
      if (isEdit && test) {
        await updateMutation.mutateAsync({
          testId: test.id,
          data: { name: data.name, mode: data.mode as TestMode },
        });
        toast.success("Test updated");
      } else {
        await createMutation.mutateAsync({
          data: { name: data.name, mode: data.mode as TestMode },
        });
        toast.success("Test created");
      }
      onOpenChange(false);
    } catch (error) {
      if (isAxiosError(error) && error.response?.status === 409) {
        setError("name", { message: "A test with this name already exists" });
        return;
      }
      toast.error("Something went wrong");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit test" : "Create test"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="name">Name</Label>
            <Input id="name" placeholder="e.g. Radio Basics" {...register("name")} />
            {errors.name ? (
              <p className="text-xs text-destructive">{errors.name.message}</p>
            ) : null}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label>Questions per session</Label>
            <Controller
              control={control}
              name="mode"
              render={({ field }) => (
                <Select
                  value={String(field.value)}
                  onValueChange={(v) => field.onChange(Number(v))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select mode" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={String(TestMode.NUMBER_30)}>
                      30 questions
                    </SelectItem>
                    <SelectItem value={String(TestMode.NUMBER_40)}>
                      40 questions
                    </SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
            {errors.mode ? (
              <p className="text-xs text-destructive">{errors.mode.message}</p>
            ) : null}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              {isEdit ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
