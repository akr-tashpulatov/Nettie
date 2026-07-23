'use client';

import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";

import { useSignUp } from "@/shared/api/generated/auth/auth";
import { ROUTES } from "@/shared/constants/routes";
import { SignUpFormData, signUpSchema } from "./sign-up-schema";
import { usePendingSignupStore } from "./pending-signup-store";

const PHONE_PREFIX = "+7";

export const useSignUpForm = () => {
  const router = useRouter();
  const setPending = usePendingSignupStore((s) => s.setPending);
  const { mutateAsync: signUp, isPending } = useSignUp();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setError,
    setValue,
    control,
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    mode: "onChange",
    defaultValues: {
      full_name: "",
      email: "",
      phone_number: PHONE_PREFIX,
      password: "",
    },
  });

  const phoneValue = useWatch({ control, name: "phone_number" });

  const onPhoneChange = (raw: string) => {
    const digits = raw.replace(/\D/g, "").replace(/^7?/, "");
    setValue("phone_number", `${PHONE_PREFIX}${digits}`, {
      shouldValidate: true,
      shouldDirty: true,
    });
  };

  const onSubmit = async (data: SignUpFormData) => {
    try {
      const { session_id } = await signUp({ data });
      setPending({ email: data.email, sessionId: session_id });
      router.push(ROUTES.VERIFY_EMAIL);
    } catch (error) {
      if (!isAxiosError(error)) {
        setError("root", { type: "server", message: "Something went wrong" });
        return;
      }
      const status = error.response?.status;
      if (status === 409) {
        setError("email", { type: "server", message: "This email is already registered" });
      } else if (status === 429) {
        setError("root", { type: "server", message: "Too many attempts, try again later" });
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
    phoneValue,
    onPhoneChange,
  };
};
