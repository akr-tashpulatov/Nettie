import { getRequestConfig } from 'next-intl/server';
import { cookies } from 'next/headers';

export default getRequestConfig(async () => {
  const cookiestore = await cookies();
  let locale = cookiestore.get('NEXT_LOCALE')?.value ?? 'ru'

  if (locale !== 'ru' && locale !== 'kk') {
    locale = 'ru'
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default
  };
});