import Image from "next/image";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { cn } from "@/shared/lib/utils";

type AuthCardProps = {
  title?: string;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  back?: { href: string; label?: string };
  align?: "center" | "left";
};

export function AuthCard({
  title,
  subtitle,
  children,
  footer,
  className,
  back,
  align = "center",
}: AuthCardProps) {
  const alignmentClass = align === "left" ? "text-left" : "text-center";

  return (
    <div className="min-h-screen w-full bg-neutral-100 flex flex-col">
      <div
        className={cn(
          "w-full max-w-sm mx-auto flex-1 flex flex-col px-6 pt-8 pb-6",
          "md:flex-none md:my-auto md:py-8",
          className,
        )}
      >
        <div className="flex justify-center">
          <Image
            src="/logo-light.svg"
            alt="Pixels"
            width={113}
            height={44}
            priority
          />
        </div>

        {back ? (
          <Link
            href={back.href}
            className="mt-8 inline-flex items-center gap-1 text-sm text-neutral-500 hover:text-neutral-800 self-start"
          >
            <ArrowLeft className="size-4" />
            {back.label ?? "Back"}
          </Link>
        ) : null}

        {title || subtitle ? (
          <div className={cn(back ? "mt-3" : "mt-6", alignmentClass)}>
            {title ? (
              <h1 className="text-2xl font-bold tracking-tight text-neutral-900">
                {title}
              </h1>
            ) : null}
            {subtitle ? (
              <p className="mt-1 text-sm text-neutral-500">{subtitle}</p>
            ) : null}
          </div>
        ) : null}

        <div className="mt-6 flex-1 md:flex-none">{children}</div>

        {footer ? <div className="mt-6">{footer}</div> : null}
      </div>
    </div>
  );
}
