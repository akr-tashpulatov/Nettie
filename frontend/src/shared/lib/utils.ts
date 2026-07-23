import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { useLocale } from "next-intl"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const localeMap: Record<string, string> = { ru: 'ru-RU', kk: 'kk-KZ' };

export function useFormatDate() {
  const locale = useLocale();
  const dateLocale = localeMap[locale] ?? 'en-US';

  return (date: Date | string, options?: Intl.DateTimeFormatOptions) =>
    new Date(date).toLocaleDateString(dateLocale, options ?? {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
}

export function getInitials(firstname: string, lastname: string): string {
  return `${firstname.charAt(0)}${lastname.charAt(0)}`.toUpperCase();
}
