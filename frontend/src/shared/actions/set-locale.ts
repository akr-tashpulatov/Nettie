'use server';

import { cookies } from "next/headers";

export type Language = 'KK' | 'RU' | 'EN';

export async function setLocale(locale: Language) {
  const cookieStore = await cookies();
  cookieStore.set('NEXT_LOCALE', locale.toLowerCase())
}