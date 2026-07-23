'use client';

import { useState } from "react";
import Link from "next/link";
import { EyeIcon, EyeOffIcon } from "lucide-react";

import { Input } from "@/shared/components/input";
import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";
import { useSignUpForm } from "../model/use-sign-up-form";
import { AuthCard } from "./auth-card";

export function SignUpPage() {
  const {
    register,
    handleSubmit,
    errors,
    isPending,
    isValid,
    phoneValue,
    onPhoneChange,
  } = useSignUpForm();

  const [showPassword, setShowPassword] = useState(false);

  return (
    <AuthCard
      title="Create account"
      subtitle="Start your IELTS journey today"
      footer={
        <p className="text-center text-sm text-neutral-500">
          Already have an account?{" "}
          <Link href={ROUTES.SIGN_IN()} className="text-neutral-900 font-semibold">
            Log in
          </Link>
        </p>
      }
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <Input
            id="full_name"
            {...register("full_name")}
            type="text"
            autoComplete="name"
            placeholder="Full name"
            aria-invalid={!!errors.full_name}
          />
          {errors.full_name ? (
            <p className="mt-1 text-xs text-red-500">{errors.full_name.message}</p>
          ) : null}
        </div>

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
            id="phone_number"
            value={phoneValue ?? ""}
            onChange={(e) => onPhoneChange(e.target.value)}
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder="Phone number"
            aria-invalid={!!errors.phone_number}
          />
          {errors.phone_number ? (
            <p className="mt-1 text-xs text-red-500">{errors.phone_number.message}</p>
          ) : null}
        </div>

        <div>
          <Input
            id="password"
            {...register("password")}
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Password (min 8 characters)"
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
          {isPending ? "Creating account..." : "Create account"}
        </button>
      </form>
    </AuthCard>
  );
}
