'use client';

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";
import { useVerifyEmailForm } from "../model/use-verify-email-form";
import { AuthCard } from "./auth-card";
import { OtpInput } from "./otp-input";

const RESEND_COOLDOWN_SECONDS = 60;

const formatCooldown = (s: number) => {
  const mm = Math.floor(s / 60);
  const ss = String(s % 60).padStart(2, "0");
  return `${mm}:${ss}`;
};

export function VerifyEmailPage() {
  const {
    email,
    code,
    setCode,
    handleSubmit,
    onResend,
    errors,
    isValid,
    isVerifying,
    isResending,
  } = useVerifyEmailForm();

  const [cooldown, setCooldown] = useState(RESEND_COOLDOWN_SECONDS);

  useEffect(() => {
    if (cooldown <= 0) return;
    const id = setInterval(() => setCooldown((s) => s - 1), 1000);
    return () => clearInterval(id);
  }, [cooldown]);

  const handleResend = async () => {
    if (cooldown > 0 || isResending) return;
    await onResend();
    setCooldown(RESEND_COOLDOWN_SECONDS);
  };

  return (
    <AuthCard
      title="Verify your email"
      subtitle={
        <>
          We sent a 6-digit code to
          <br />
          <span className="font-semibold text-neutral-900">{email}</span>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <OtpInput value={code ?? ""} onChange={setCode} invalid={!!errors.code} />
        {errors.code ? (
          <p className="text-center text-xs text-red-500">{errors.code.message}</p>
        ) : null}
        {errors.root ? (
          <p className="text-center text-sm text-red-500">{errors.root.message}</p>
        ) : null}

        <button
          type="submit"
          disabled={!isValid || isVerifying}
          className={cn(
            "mt-2 w-full h-12 rounded-full flex items-center justify-center font-semibold text-sm transition",
            "bg-[#C8F53C] text-black hover:bg-[#C8F53C]/90",
            "disabled:bg-neutral-200 disabled:text-neutral-400",
          )}
        >
          {isVerifying ? "Verifying..." : "Verify Email"}
        </button>

        <p className="text-center text-xs text-neutral-500">
          Didn&apos;t receive the code?{" "}
          <button
            type="button"
            onClick={handleResend}
            disabled={cooldown > 0 || isResending}
            className="font-semibold text-[#3A8A00] disabled:text-neutral-400 disabled:cursor-not-allowed"
          >
            {cooldown > 0 ? `Resend in ${formatCooldown(cooldown)}` : "Resend"}
          </button>
        </p>
        <p className="-mt-3 text-center text-xs text-neutral-400">
          Expires in 10 min · Check spam
        </p>

        <div className="text-center mt-2">
          <Link
            href={ROUTES.SIGN_UP}
            className="inline-flex items-center gap-1 text-sm text-neutral-500 hover:text-neutral-800"
          >
            <ArrowLeft className="size-4" />
            Back
          </Link>
        </div>
      </form>
    </AuthCard>
  );
}
