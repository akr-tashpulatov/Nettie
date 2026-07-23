import { Suspense } from "react";
import { VerifyEmailPage } from "@/features/auth/ui/verify-email-page";

export default function Page() {
  return (
    <Suspense>
      <VerifyEmailPage />
    </Suspense>
  );
}
