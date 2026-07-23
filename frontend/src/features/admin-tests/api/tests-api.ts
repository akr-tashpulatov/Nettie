'use client';

import { useQueryClient } from "@tanstack/react-query";

import {
  useListTests,
  useCreateTest,
  useGetTest,
  useUpdateTest,
  useDeleteTest,
  useImportQuestions,
  useAddQuestion,
  useListQuestions,
  useUpdateQuestion,
  useDeleteQuestion,
  getListTestsQueryKey,
  getGetTestQueryKey,
  getListQuestionsQueryKey,
} from "@/shared/api/generated/tests-admin/tests-admin";
import type { ListTestsParams } from "@/shared/api/generated/model";

const STALE_TIME = 60 * 1000;

export const useTestsQuery = (params?: ListTestsParams) =>
  useListTests(params, { query: { staleTime: STALE_TIME } });

export const useTestQuery = (testId: number) =>
  useGetTest(testId, {
    query: { staleTime: STALE_TIME, enabled: Number.isFinite(testId) },
  });

export const useQuestionsQuery = (testId: number) =>
  useListQuestions(testId, {
    query: { staleTime: STALE_TIME, enabled: Number.isFinite(testId) },
  });

export const useCreateTestMutation = () => {
  const queryClient = useQueryClient();
  return useCreateTest({
    mutation: {
      onSuccess: () =>
        queryClient.invalidateQueries({ queryKey: getListTestsQueryKey() }),
    },
  });
};

export const useUpdateTestMutation = () => {
  const queryClient = useQueryClient();
  return useUpdateTest({
    mutation: {
      onSuccess: (_data, { testId }) => {
        queryClient.invalidateQueries({ queryKey: getListTestsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getGetTestQueryKey(testId) });
      },
    },
  });
};

export const useDeleteTestMutation = () => {
  const queryClient = useQueryClient();
  return useDeleteTest({
    mutation: {
      onSuccess: () =>
        queryClient.invalidateQueries({ queryKey: getListTestsQueryKey() }),
    },
  });
};

const invalidateTest = (queryClient: ReturnType<typeof useQueryClient>, testId: number) => {
  queryClient.invalidateQueries({ queryKey: getListQuestionsQueryKey(testId) });
  queryClient.invalidateQueries({ queryKey: getGetTestQueryKey(testId) });
  queryClient.invalidateQueries({ queryKey: getListTestsQueryKey() });
};

export const useImportQuestionsMutation = () => {
  const queryClient = useQueryClient();
  return useImportQuestions({
    mutation: {
      onSuccess: (_data, { testId }) => invalidateTest(queryClient, testId),
    },
  });
};

export const useAddQuestionMutation = () => {
  const queryClient = useQueryClient();
  return useAddQuestion({
    mutation: {
      onSuccess: (_data, { testId }) => invalidateTest(queryClient, testId),
    },
  });
};

export const useUpdateQuestionMutation = () => {
  const queryClient = useQueryClient();
  return useUpdateQuestion({
    mutation: {
      onSuccess: (_data, { testId }) => invalidateTest(queryClient, testId),
    },
  });
};

export const useDeleteQuestionMutation = () => {
  const queryClient = useQueryClient();
  return useDeleteQuestion({
    mutation: {
      onSuccess: (_data, { testId }) => invalidateTest(queryClient, testId),
    },
  });
};
