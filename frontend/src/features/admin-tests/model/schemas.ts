import { z } from "zod";

import { TestMode } from "@/shared/api/generated/model";

export const testFormSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255, "Name is too long"),
  mode: z.union([z.literal(TestMode.NUMBER_30), z.literal(TestMode.NUMBER_40)], {
    message: "Choose a session mode",
  }),
});

export type TestFormData = z.infer<typeof testFormSchema>;

export const questionFormSchema = z
  .object({
    text: z.string().trim().min(1, "Question text is required"),
    correctIndex: z.number().int().min(0),
    options: z
      .array(z.object({ text: z.string().trim().min(1, "Option cannot be empty") }))
      .min(2, "Add at least two options"),
  })
  .refine((data) => data.correctIndex < data.options.length, {
    message: "Select the correct answer",
    path: ["correctIndex"],
  });

export type QuestionFormData = z.infer<typeof questionFormSchema>;
