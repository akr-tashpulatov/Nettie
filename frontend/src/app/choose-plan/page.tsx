import { Suspense } from "react";
import { ChoosePlanPage } from "@/features/subscription/ui/choose-plan-page";

export default function Page() {
  return (
    <Suspense>
      <ChoosePlanPage />
    </Suspense>
  );
}
