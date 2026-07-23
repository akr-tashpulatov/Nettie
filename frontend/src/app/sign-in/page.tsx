import { Suspense } from "react";
import { SignInPage } from "@/features/auth/ui/sign-in-page";

export default function Page() {
  return (
    <Suspense>
      <SignInPage />
    </Suspense>
  );
}
