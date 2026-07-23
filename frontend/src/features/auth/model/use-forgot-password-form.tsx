'use client';

import { useState } from "react";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useRequestResetPassword } from "@/shared/api/generated/auth/auth";
import {
  ForgotPasswordFormData,
  forgotPasswordSchema,
} from "./forgot-password-schema";

export const useForgotPasswordForm = () => {
  const { mutateAsync: requestReset, isPending } = useRequestResetPassword();
  const [sentToEmail, setSentToEmail] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setError,
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    mode: "onChange",
    defaultValues: { email: "" },
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      await requestReset({ data });
      setSentToEmail(data.email);
      toast.success("Reset link sent");
    } catch (error) {
      if (!isAxiosError(error)) {
        setError("root", { type: "server", message: "Something went wrong" });
        return;
      }
      const status = error.response?.status;
      if (status === 404) {
        setError("email", {
          type: "server",
          message: "No account found with this email",
        });
      } else if (status === 429) {
        setError("root", {
          type: "server",
          message: "Too many attempts, try again later",
        });
      } else {
        setError("root", { type: "server", message: "Something went wrong" });
        toast.error("Something went wrong");
      }
    }
  };

  return {
    register,
    handleSubmit: handleSubmit(onSubmit),
    errors,
    isPending,
    isValid,
    sentToEmail,
  };
};
