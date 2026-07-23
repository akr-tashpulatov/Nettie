import z from "zod";

export const verifyEmailSchema = z.object({
  code: z
    .string()
    .length(6, "Enter the 6-digit code")
    .regex(/^\d{6}$/, "Code must be 6 digits"),
});

export type VerifyEmailFormData = z.infer<typeof verifyEmailSchema>;
