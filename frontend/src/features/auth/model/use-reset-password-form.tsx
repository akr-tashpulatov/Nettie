'use client';

import { useState } from "react";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSearchParams } from "next/navigation";

import { useConfirmResetPassword } from "@/shared/api/generated/auth/auth";
import {
  ResetPasswordFormData,
  resetPasswordSchema,
} from "./reset-password-schema";

export const useResetPasswordForm = () => {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const { mutateAsync: confirm, isPending } = useConfirmResetPassword();
  const [saved, setSaved] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setError,
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    mode: "onChange",
    defaultValues: { password: "", confirm: "" },
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setError("root", { type: "server", message: "Reset link is invalid" });
      return;
    }
    try {
      await confirm({
        data: { reset_token: token, new_password: data.password },
      });
      setSaved(true);
    } catch (error) {
      if (!isAxiosError(error)) {
        setError("root", { type: "server", message: "Something went wrong" });
        return;
      }
      const status = error.response?.status;
      if (status === 400 || status === 401) {
        setError("root", {
          type: "server",
          message: "Reset link is invalid or expired",
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
    hasToken: !!token,
    saved,
  };
};
