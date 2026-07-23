'use client';

import Link from "next/link";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";

import { Input } from "@/shared/components/input";
import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";
import { useForgotPasswordForm } from "../model/use-forgot-password-form";
import { AuthCard } from "./auth-card";

const STEPS = [
  "Open your email app",
  "Click the link — valid for 1 hour",
  "Set a new password and log in",
];

export function ForgotPasswordPage() {
  const { register, handleSubmit, errors, isPending, isValid, sentToEmail } =
    useForgotPasswordForm();

  if (sentToEmail) {
    return (
      <AuthCard align="center">
        <div className="flex flex-col items-center -mt-2">
          <div className="w-14 h-14 rounded-full bg-[#C8F53C]/25 flex items-center justify-center">
            <Check className="size-6 text-[#3A8A00]" strokeWidth={3} />
          </div>
          <h2 className="mt-4 text-2xl font-bold tracking-tight text-neutral-900">
            Check your email
          </h2>
          <p className="mt-2 text-sm text-neutral-500">
            Link sent to{" "}
            <span className="text-[#3A8A00] font-medium">{sentToEmail}</span>
          </p>
          <p className="mt-1 text-xs text-neutral-400">
            If email is registered, you&apos;ll receive a reset link.
          </p>

          <ol className="mt-6 w-full bg-white rounded-2xl shadow-sm border border-neutral-100 p-4 flex flex-col gap-3">
            {STEPS.map((step, i) => (
              <li key={i} className="flex items-center gap-3 text-sm text-neutral-700">
                <span className="w-6 h-6 rounded-full bg-[#C8F53C] text-black text-xs font-bold flex items-center justify-center shrink-0">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>

          <Link
            href={`${ROUTES.RESET_PASSWORD}?token=demo`}
            className="mt-6 w-full h-12 rounded-full flex items-center justify-center gap-2 font-semibold text-sm bg-neutral-200 text-neutral-500 hover:bg-neutral-300 transition"
          >
            Demo: simulate link click
            <ArrowRight className="size-4" />
          </Link>

          <Link
            href={ROUTES.SIGN_IN()}
            className="mt-4 inline-flex items-center gap-1 text-sm text-neutral-500 hover:text-neutral-800"
          >
            <ArrowLeft className="size-4" />
            Back to Log in
          </Link>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title="Forgot password?"
      subtitle="Enter your email and we'll send you a reset link."
      back={{ href: ROUTES.SIGN_IN() }}
      align="left"
      footer={
        <p className="text-center text-sm text-neutral-500">
          Remember it after all?{" "}
          <Link href={ROUTES.SIGN_IN()} className="text-neutral-900 font-semibold">
            Log in
          </Link>
        </p>
      }
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <Input
            id="email"
            {...register("email")}
            type="email"
            autoComplete="email"
            placeholder="Email address"
            aria-invalid={!!errors.email}
          />
          {errors.email ? (
            <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
          ) : null}
        </div>

        {errors.root ? (
          <p className="text-sm text-red-500">{errors.root.message}</p>
        ) : null}

        <button
          type="submit"
          disabled={!isValid || isPending}
          className={cn(
            "mt-2 w-full h-12 rounded-full flex items-center justify-center font-semibold text-sm transition",
            "bg-[#C8F53C] text-black hover:bg-[#C8F53C]/90",
            "disabled:bg-neutral-200 disabled:text-neutral-400",
          )}
        >
          {isPending ? "Sending..." : "Send Reset Link"}
        </button>
      </form>
    </AuthCard>
  );
}
