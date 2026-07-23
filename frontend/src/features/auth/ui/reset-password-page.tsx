'use client';

import { useState } from "react";
import Link from "next/link";
import { Check, EyeIcon, EyeOffIcon } from "lucide-react";

import { Input } from "@/shared/components/input";
import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";
import { useResetPasswordForm } from "../model/use-reset-password-form";
import { AuthCard } from "./auth-card";

export function ResetPasswordPage() {
  const { register, handleSubmit, errors, isPending, isValid, saved } =
    useResetPasswordForm();
  const [showPassword, setShowPassword] = useState(false);

  if (saved) {
    return (
      <AuthCard align="center">
        <div className="flex flex-col items-center -mt-2">
          <div className="w-14 h-14 rounded-full bg-[#C8F53C]/25 flex items-center justify-center">
            <Check className="size-6 text-[#3A8A00]" strokeWidth={3} />
          </div>
          <h2 className="mt-4 text-2xl font-bold tracking-tight text-neutral-900">
            Password updated!
          </h2>
          <p className="mt-2 text-sm text-neutral-500 text-center">
            Your new password has been saved. You can now log in.
          </p>
          <Link
            href={ROUTES.SIGN_IN()}
            className={cn(
              "mt-6 w-full h-12 rounded-full flex items-center justify-center font-semibold text-sm transition",
              "bg-[#C8F53C] text-black hover:bg-[#C8F53C]/90",
            )}
          >
            Go to Log in
          </Link>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title="New password"
      subtitle="Choose a strong password for your account"
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <Input
            id="password"
            {...register("password")}
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="New password (min 8 characters)"
            rightIcon={
              showPassword ? (
                <EyeIcon
                  className="cursor-pointer size-4"
                  onClick={() => setShowPassword(false)}
                />
              ) : (
                <EyeOffIcon
                  className="cursor-pointer size-4"
                  onClick={() => setShowPassword(true)}
                />
              )
            }
            aria-invalid={!!errors.password}
          />
          {errors.password ? (
            <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
          ) : null}
        </div>

        <div>
          <Input
            id="confirm"
            {...register("confirm")}
            type="password"
            autoComplete="new-password"
            placeholder="Confirm new password"
            aria-invalid={!!errors.confirm}
          />
          {errors.confirm ? (
            <p className="mt-1 text-xs text-red-500">{errors.confirm.message}</p>
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
          {isPending ? "Saving..." : "Set new password"}
        </button>
      </form>
    </AuthCard>
  );
}
