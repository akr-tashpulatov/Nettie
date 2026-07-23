'use client';

import { useQuery } from "@tanstack/react-query";

import {
  getGetTariffsQueryKey,
  getTariffs,
} from "@/shared/api/generated/tariffs/tariffs";

export const useGetTariffsQuery = () =>
  useQuery({
    queryKey: getGetTariffsQueryKey(),
    queryFn: ({ signal }) => getTariffs(undefined, signal),
    staleTime: 60_000,
  });
