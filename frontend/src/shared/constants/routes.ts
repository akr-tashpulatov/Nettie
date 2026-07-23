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

  // Admin
  ADMIN_TESTS: "/admin/tests",
  ADMIN_TEST: (id: number | string) => `/admin/tests/${id}`,

  // Student
  STUDENT_TESTS: "/student/tests",
  STUDENT_SESSIONS: "/student/sessions",
  STUDENT_SESSION: (id: number | string) => `/student/sessions/${id}`,
}
