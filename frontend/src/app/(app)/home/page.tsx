'use client';

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { ROUTES } from "@/shared/constants/routes";
import { Role } from "@/shared/api/generated/model/role";
import { useAuth } from "@/shared/session/auth-provider";
import { LoadingSpinner } from "@/shared/components/loading-spinner";

export default function HomePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (user?.role === Role.ADMIN) {
      router.replace(ROUTES.ADMIN_TESTS);
    } else {
      router.replace(ROUTES.STUDENT_TESTS);
    }
  }, [isLoading, user, router]);

  return (
    <div className="flex justify-center py-20">
      <LoadingSpinner />
    </div>
  );
}
