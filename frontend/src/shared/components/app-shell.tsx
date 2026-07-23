'use client';

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut } from "lucide-react";

import { APP_NAME } from "@/shared/constants/app";
import { ROUTES } from "@/shared/constants/routes";
import { Role } from "@/shared/api/generated/model/role";
import { useSignOut } from "@/shared/api/generated/auth/auth";
import { useAuth } from "@/shared/session/auth-provider";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";

interface NavItem {
  href: string;
  label: string;
}

const ADMIN_NAV: NavItem[] = [{ href: ROUTES.ADMIN_TESTS, label: "Tests" }];
const STUDENT_NAV: NavItem[] = [
  { href: ROUTES.STUDENT_TESTS, label: "Take a test" },
  { href: ROUTES.STUDENT_SESSIONS, label: "My results" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, clearSession } = useAuth();
  const { mutateAsync: signOut, isPending } = useSignOut();
  const router = useRouter();
  const pathname = usePathname();

  const nav = user?.role === Role.ADMIN ? ADMIN_NAV : STUDENT_NAV;

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch {
      // best-effort: clear the local session regardless of server outcome
    } finally {
      clearSession();
      router.replace(ROUTES.SIGN_IN());
    }
  };

  return (
    <div className="min-h-screen bg-muted/30">
      <header className="sticky top-0 z-30 border-b bg-background">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-6 px-4">
          <Link href={ROUTES.HOME} className="font-semibold">
            {APP_NAME}
          </Link>

          <nav className="flex items-center gap-1">
            {nav.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="ml-auto flex items-center gap-3">
            {user ? (
              <span className="hidden text-sm text-muted-foreground sm:inline">
                {user.full_name}
              </span>
            ) : null}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSignOut}
              isLoading={isPending}
            >
              <LogOut className="size-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
    </div>
  );
}
