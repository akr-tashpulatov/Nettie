'use client';

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Check, Lock, X } from "lucide-react";
import toast from "react-hot-toast";

import { useCheckout } from "@/shared/api/generated/subscription/subscription";
import type { TariffResponse } from "@/shared/api/generated/model/tariff-response";
import type { DurationResponse } from "@/shared/api/generated/model/duration-response";
import { ROUTES } from "@/shared/constants/routes";
import { cn } from "@/shared/lib/utils";
import { useGetTariffsQuery } from "../api/tariffs-api";

const POPULAR_CODE = "pro";

const CURRENCY_SYMBOL: Record<string, string> = {
  KZT: "₸",
  USD: "$",
  EUR: "€",
  RUB: "₽",
};

const formatPrice = (value: string, currency: string) => {
  const n = Number(value);
  if (Number.isNaN(n)) return `${value} ${currency}`;
  const formatted = n.toLocaleString("ru-RU").replace(/,/g, " ");
  return `${formatted} ${CURRENCY_SYMBOL[currency] ?? currency}`;
};

const formatDuration = (d: DurationResponse) => {
  if (d.unit === "MONTHS") return d.value === 1 ? "/mo" : `/${d.value}mo`;
  if (d.unit === "DAYS") return d.value === 1 ? "/day" : `/${d.value}d`;
  if (d.unit === "HOURS") return d.value === 1 ? "/hr" : `/${d.value}h`;
  return "";
};

export function ChoosePlanPage() {
  const router = useRouter();
  const { data: tariffs, isLoading } = useGetTariffsQuery();
  const { mutateAsync: startCheckout, isPending: isCheckingOut } = useCheckout();

  const initialSelectedId = useMemo(() => {
    if (!tariffs?.length) return null;
    const popular = tariffs.find((t) => t.code.toLowerCase() === POPULAR_CODE);
    return (popular ?? tariffs[0]).id;
  }, [tariffs]);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const activeId = selectedId ?? initialSelectedId;
  const selected = tariffs?.find((t) => t.id === activeId);

  const onClose = () => router.push(ROUTES.HOME);

  const onChoose = async () => {
    if (!selected) return;
    try {
      const res = await startCheckout({ data: { tariff_id: selected.id } });
      const url = (res as { url?: string })?.url;
      if (url) window.location.href = url;
      else toast.success("Redirecting to payment...");
    } catch {
      toast.error("Could not start checkout");
    }
  };

  return (
    <div className="min-h-screen w-full bg-neutral-100 flex justify-center">
      <div className="w-full max-w-sm min-h-screen bg-white flex flex-col px-6 pt-6 pb-6 relative">
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="absolute top-4 right-4 text-neutral-400 hover:text-neutral-800"
        >
          <X className="size-5" />
        </button>

        <div className="text-center mt-6">
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900">
            Choose your plan
          </h1>
          <p className="mt-1 text-sm text-neutral-500">
            Start practising today. Cancel anytime.
          </p>
        </div>

        <div className="mt-6 flex flex-col gap-3 flex-1">
          {isLoading ? (
            <>
              <PlanSkeleton />
              <PlanSkeleton />
              <PlanSkeleton />
            </>
          ) : tariffs?.length ? (
            tariffs.map((tariff) => (
              <PlanCard
                key={tariff.id}
                tariff={tariff}
                selected={tariff.id === activeId}
                popular={tariff.code.toLowerCase() === POPULAR_CODE}
                onSelect={() => setSelectedId(tariff.id)}
              />
            ))
          ) : (
            <p className="text-center text-sm text-neutral-500 py-8">
              No plans available.
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={onChoose}
          disabled={!selected || isCheckingOut}
          className={cn(
            "mt-4 w-full h-12 rounded-full flex items-center justify-center gap-2 font-semibold text-sm transition",
            "bg-[#C8F53C] text-black hover:bg-[#C8F53C]/90",
            "disabled:bg-neutral-200 disabled:text-neutral-400",
          )}
        >
          {isCheckingOut
            ? "Loading..."
            : selected
              ? `Choose ${selected.name}`
              : "Choose plan"}
          <ArrowRight className="size-4" />
        </button>

        <p className="mt-3 flex items-center justify-center gap-1.5 text-xs text-neutral-400">
          <Lock className="size-3" />
          Secure payment · Cancel anytime
        </p>
      </div>
    </div>
  );
}

type PlanCardProps = {
  tariff: TariffResponse;
  selected: boolean;
  popular: boolean;
  onSelect: () => void;
};

function PlanCard({ tariff, selected, popular, onSelect }: PlanCardProps) {
  const hasDiscount = !!tariff.discount_price;
  const currentPrice = hasDiscount
    ? tariff.discount_price!
    : tariff.base_price;

  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        "text-left rounded-2xl border-2 bg-white p-4 transition",
        selected
          ? "border-[#C8F53C] shadow-sm"
          : "border-neutral-200 hover:border-neutral-300",
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-full bg-neutral-100 text-xs font-semibold text-neutral-800">
            {tariff.name}
          </span>
          {popular ? (
            <span className="px-2.5 py-1 rounded-full bg-[#C8F53C]/40 text-xs font-semibold text-[#3A8A00]">
              Popular
            </span>
          ) : null}
        </div>
        <div className="text-right">
          {hasDiscount ? (
            <span className="text-xs text-neutral-400 line-through mr-1">
              {formatPrice(tariff.base_price, tariff.currency)}
            </span>
          ) : null}
          <span className="text-sm font-bold text-neutral-900">
            {formatPrice(currentPrice, tariff.currency)}
          </span>
          <span className="text-xs text-neutral-400">
            {formatDuration(tariff.duration)}
          </span>
        </div>
      </div>
      <ul className="mt-3 flex flex-col gap-1.5">
        {tariff.items.map((item) => (
          <li
            key={item.code}
            className="flex items-center gap-2 text-sm text-neutral-700"
          >
            <Check className="size-4 text-[#3A8A00]" strokeWidth={3} />
            {item.name}
          </li>
        ))}
      </ul>
    </button>
  );
}

function PlanSkeleton() {
  return (
    <div className="h-40 rounded-2xl border-2 border-neutral-200 bg-neutral-50 animate-pulse" />
  );
}
