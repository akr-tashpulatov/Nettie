'use client';

import { ReactNode } from 'react';
import { queryClient } from '@/shared/api/query-client';
import { QueryClientProvider } from '@tanstack/react-query';

interface ProvidersProps {
  children: ReactNode;
}

export function QueryProvider({ children }: ProvidersProps) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
