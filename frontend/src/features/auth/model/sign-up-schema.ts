import z from "zod";

const RU_PHONE_DIGITS = 11;

export const signUpSchema = z.object({
  full_name: z.string().min(2, "Full name is too short"),
  email: z.email("Enter a valid email"),
  phone_number: z
    .string()
    .refine(
      (v) => v.startsWith("+7") && v.replace(/\D/g, "").length === RU_PHONE_DIGITS,
      "Enter a valid phone number",
    ),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export type SignUpFormData = z.infer<typeof signUpSchema>;
