'use client';

import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";

import { useSignIn } from "@/shared/api/generated/auth/auth";
import { useAuth } from "@/shared/session/auth-provider";
import { ROUTES } from "@/shared/constants/routes";
import { SignInFormData, signInSchema } from "./sign-in-schema";

export const useSignInForm = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setSession } = useAuth();
  const { mutateAsync: signIn, isPending } = useSignIn();

  const redirectRoute = searchParams.get("redirect") || ROUTES.HOME;

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setError,
  } = useForm<SignInFormData>({
    resolver: zodResolver(signInSchema),
    mode: "onChange",
  });

  const onSubmit = async (data: SignInFormData) => {
    try {
      const { access_token } = await signIn({ data });
      setSession(access_token);
      toast.success("Signed in");
      router.push(redirectRoute);
    } catch (error) {
      if (!isAxiosError(error)) {
        setError("root", { type: "server", message: "Something went wrong" });
        return;
      }

      const status = error.response?.status;
      if (status === 401) {
        setError("root", { type: "server", message: "Incorrect email or password" });
      } else if (status === 429) {
        setError("root", { type: "server", message: "Too many login attempts, try again later" });
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
  };
};
