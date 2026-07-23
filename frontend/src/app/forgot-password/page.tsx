import { Suspense } from "react";
import { ForgotPasswordPage } from "@/features/auth/ui/forgot-password-page";

export default function Page() {
  return (
    <Suspense>
      <ForgotPasswordPage />
    </Suspense>
  );
}
