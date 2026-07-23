import { Suspense } from "react";
import { SignUpPage } from "@/features/auth/ui/sign-up-page";

export default function Page() {
  return (
    <Suspense>
      <SignUpPage />
    </Suspense>
  );
}
