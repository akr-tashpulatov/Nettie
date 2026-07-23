export const ROUTES = {
  HOME: "/home",
  SIGN_IN: (redirect?: string | null) => {
    return redirect ?
      `/sign-in?redirect=${encodeURIComponent(redirect)}` :
      "/sign-in"
  },
  SIGN_UP: "/sign-up",
  VERIFY_EMAIL: "/verify-email",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
  CHOOSE_PLAN: "/choose-plan",
}