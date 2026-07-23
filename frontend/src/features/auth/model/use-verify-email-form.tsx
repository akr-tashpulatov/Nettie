'use client';

import { useEffect } from "react";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";

import {
  useResendCode,
  useSignUpVerify,
} from "@/shared/api/generated/auth/auth";
import { useAuth } from "@/shared/session/auth-provider";
import { ROUTES } from "@/shared/constants/routes";
import { VerifyEmailFormData, verifyEmailSchema } from "./verify-email-schema";
import { usePendingSignupStore } from "./pending-signup-store";

export const useVerifyEmailForm = () => {
  const router = useRouter();
  const { setSession } = useAuth();
  const pending = usePendingSignupStore((s) => s.pending);
  const updateSessionId = usePendingSignupStore((s) => s.updateSessionId);
  const clearPending = usePendingSignupStore((s) => s.clear);

  const { mutateAsync: verify, isPending: isVerifying } = useSignUpVerify();
  const { mutateAsync: resend, isPending: isResending } = useResendCode();

  useEffect(() => {
    if (!pending) router.replace(ROUTES.SIGN_UP);
  }, [pending, router]);

  const {
    handleSubmit,
    formState: { errors, isValid },
    setError,
    setValue,
    control,
  } = useForm<VerifyEmailFormData>({
    resolver: zodResolver(verifyEmailSchema),
    mode: "onChange",
    defaultValues: { code: "" },
  });

  const code = useWatch({ control, name: "code" });

  const onSubmit = async (data: VerifyEmailFormData) => {
    if (!pending) return;
    try {
      const res = await verify({
        data: { session_id: pending.sessionId, otp_code: Number(data.code) },
      });
      if (!res.success) {
        setError("code", {
          type: "server",
          message: res.code_invalidated
            ? "Code expired, request a new one"
            : "Invalid code",
        });
        return;
      }
      if (res.access_token) setSession(res.access_token);
      clearPending();
      toast.success("Email verified");
      router.push(ROUTES.HOME);
    } catch (error) {
      if (!isAxiosError(error)) {
        setError("root", { type: "server", message: "Something went wrong" });
        return;
      }
      setError("root", { type: "server", message: "Verification failed" });
    }
  };

  const onResend = async () => {
    if (!pending) return;
    try {
      const res = await resend({ data: { session_id: pending.sessionId } });
      updateSessionId(res.session_id);
      toast.success("Code sent");
    } catch {
      toast.error("Could not resend code");
    }
  };

  return {
    email: pending?.email ?? "",
    code,
    setCode: (value: string) =>
      setValue("code", value, { shouldValidate: true, shouldDirty: true }),
    handleSubmit: handleSubmit(onSubmit),
    onResend,
    errors,
    isValid,
    isVerifying,
    isResending,
  };
};
