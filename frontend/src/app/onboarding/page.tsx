"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ArrowRight } from "lucide-react";

import { slides } from "@/shared/constants/onboarding";
import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";

const ONBOARDING_STORAGE_KEY = "pixels:onboardingCompleted";
const SWIPE_THRESHOLD_PX = 50;

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const dragStartX = useRef<number | null>(null);

  useEffect(() => {
    if (localStorage.getItem(ONBOARDING_STORAGE_KEY) === "true") {
      router.replace(ROUTES.SIGN_IN());
    }
  }, [router]);

  const finish = () => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, "true");
    router.replace(ROUTES.SIGN_IN());
  };

  const currentStep = slides[step];
  const isLast = step === slides.length - 1;

  const handleNext = () => (isLast ? finish() : setStep((s) => s + 1));

  const onPointerDown = (e: React.PointerEvent) => {
    dragStartX.current = e.clientX;
  };

  const onPointerUp = (e: React.PointerEvent) => {
    if (dragStartX.current === null) return;
    const delta = e.clientX - dragStartX.current;
    dragStartX.current = null;
    if (Math.abs(delta) < SWIPE_THRESHOLD_PX) return;
    if (delta < 0 && !isLast) setStep((s) => s + 1);
    if (delta > 0 && step > 0) setStep((s) => s - 1);
  };

  return (
    <div className="relative bg-[#0D0D1A] w-full min-h-screen flex flex-col text-white">
      <div className="w-full flex items-center justify-between px-6 py-6">
        <Image src="/logo.svg" alt="Pixels" width={82} height={24} priority />
        {isLast ? null : (
          <button
            type="button"
            onClick={finish}
            className="rounded-full bg-white/10 px-4 py-1.5 text-sm text-white/80 hover:bg-white/15 transition"
          >
            Skip
          </button>
        )}
      </div>

      <div
        className="w-full max-w-sm mx-auto flex-1 flex flex-col px-6 pb-6 touch-pan-y select-none"
        onPointerDown={onPointerDown}
        onPointerUp={onPointerUp}
      >
        <div className="flex-1 flex items-center justify-center py-8">
          <Image
            key={currentStep.key}
            src={currentStep.img_url}
            alt={currentStep.title}
            width={280}
            height={280}
            priority
            draggable={false}
            className="pointer-events-none"
          />
        </div>

        <div
          className="flex justify-center gap-2 mb-6"
          role="tablist"
          aria-label="Onboarding slides"
        >
          {slides.map((s, i) => {
            const active = i === step;
            return (
              <button
                key={s.key}
                type="button"
                role="tab"
                aria-selected={active}
                aria-label={`Go to slide ${i + 1}`}
                onClick={() => setStep(i)}
                className={cn(
                  "h-2 rounded-full transition-all",
                  active
                    ? s.color === "pink"
                      ? "w-6 bg-[#EC6ED2]"
                      : "w-6 bg-[#C8F53C]"
                    : "w-2 bg-white/25 hover:bg-white/40"
                )}
              />
            );
          })}
        </div>

        <div className="text-center px-2 mb-6">
          <h1 className="text-2xl font-bold tracking-tight">
            {currentStep.title}
          </h1>
          <p className="mt-3 text-sm text-white/60 leading-relaxed">
            {currentStep.subtitle}
          </p>
        </div>

        <button
          type="button"
          onClick={handleNext}
          className={cn(
            "w-full h-12 rounded-full flex items-center justify-center gap-2 font-semibold text-sm transition active:scale-[0.98]",
            currentStep.color === "pink"
              ? "bg-[#EC6ED2] text-white hover:bg-[#EC6ED2]/90"
              : "bg-[#C8F53C] text-black hover:bg-[#C8F53C]/90"
          )}
        >
          {isLast ? "Get started" : "Next"}
          <ArrowRight className="size-4" />
        </button>

        <p className="mt-4 text-center text-sm text-white/60">
          Already have an account?{" "}
          <Link href={ROUTES.SIGN_IN()} className="text-white font-semibold">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
