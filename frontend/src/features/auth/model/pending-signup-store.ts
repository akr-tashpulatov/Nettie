import { create } from "zustand";

type PendingSignup = {
  email: string;
  sessionId: string;
};

type PendingSignupState = {
  pending: PendingSignup | null;
  setPending: (value: PendingSignup) => void;
  updateSessionId: (sessionId: string) => void;
  clear: () => void;
};

export const usePendingSignupStore = create<PendingSignupState>((set) => ({
  pending: null,
  setPending: (pending) => set({ pending }),
  updateSessionId: (sessionId) =>
    set((state) =>
      state.pending ? { pending: { ...state.pending, sessionId } } : state,
    ),
  clear: () => set({ pending: null }),
}));
