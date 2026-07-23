'use client';

import { useState } from "react";
import Link from "next/link";
import { EyeIcon, EyeOffIcon } from "lucide-react";

import { Input } from "@/shared/components/input";
import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";
import { useSignInForm } from "../model/use-sign-in-form";
import { AuthCard } from "./auth-card";

export function SignInPage() {
  const { register, handleSubmit, errors, isPending, isValid } = useSignInForm();
  const [showPassword, setShowPassword] = useState(false);

  return (
    <AuthCard
      title="Welcome back"
      subtitle="Log in to continue practising"
      footer={
        <p className="text-center text-sm text-neutral-500">
          Don&apos;t have an account?{" "}
          <Link href={ROUTES.SIGN_UP} className="text-neutral-900 font-semibold">
            Sign up
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
            placeholder="Email"
            aria-invalid={!!errors.email}
          />
          {errors.email ? (
            <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
          ) : null}
        </div>

        <div>
          <Input
            id="password"
            {...register("password")}
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            placeholder="Password"
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
          <div className="mt-1 flex justify-end">
            <Link href={ROUTES.FORGOT_PASSWORD} className="text-xs font-semibold text-[#3A8A00]">
              Forgot password?
            </Link>
          </div>
          {errors.password ? (
            <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
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
          {isPending ? "Signing in..." : "Log In"}
        </button>

        <div className="flex items-center gap-3 my-2">
          <div className="h-px flex-1 bg-neutral-200" />
          <span className="text-xs text-neutral-400">or</span>
          <div className="h-px flex-1 bg-neutral-200" />
        </div>
      </form>
    </AuthCard>
  );
}
