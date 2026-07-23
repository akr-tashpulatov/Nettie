'use client';

import { useQueryClient } from "@tanstack/react-query";

import { useListAvailableTests } from "@/shared/api/generated/tests-student/tests-student";
import {
  useStartSession,
  useListSessions,
  useGetSessionDetail,
  useAnswerQuestion,
  getListSessionsQueryKey,
  getGetSessionDetailQueryKey,
} from "@/shared/api/generated/exam-sessions-student/exam-sessions-student";
import type {
  ListAvailableTestsParams,
  ListSessionsParams,
} from "@/shared/api/generated/model";

const STALE_TIME = 60 * 1000;

export const useAvailableTestsQuery = (params?: ListAvailableTestsParams) =>
  useListAvailableTests(params, { query: { staleTime: STALE_TIME } });

export const useSessionsQuery = (params?: ListSessionsParams) =>
  useListSessions(params, { query: { staleTime: STALE_TIME } });

export const useSessionQuery = (sessionId: number) =>
  useGetSessionDetail(sessionId, {
    query: { staleTime: 0, enabled: Number.isFinite(sessionId) },
  });

export const useStartSessionMutation = () => {
  const queryClient = useQueryClient();
  return useStartSession({
    mutation: {
      onSuccess: () =>
        queryClient.invalidateQueries({ queryKey: getListSessionsQueryKey() }),
    },
  });
};

export const useAnswerQuestionMutation = () => useAnswerQuestion();

export { getGetSessionDetailQueryKey };
