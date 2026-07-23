import { ROUTES } from "@/shared/constants/routes";
import { AuthProxy } from "@/shared/proxy/auth.proxy";
import { Role } from "@/shared/api/generated/model/role";
import { NextRequest, NextResponse } from "next/server";

const publicRoutes = ['/sign-in', '/']

// Prefix-matched protected areas with the role they require.
const roleGuardedPrefixes: { prefix: string; roles?: Role[] }[] = [
  { prefix: '/home' },
  { prefix: '/admin', roles: [Role.ADMIN] },
  { prefix: '/student', roles: [Role.STUDENT] },
]

export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const isPublicRoute = publicRoutes.includes(path)

  if (path.includes('/sign-in')) {
    const authProxy = new AuthProxy(request);
    const authResponse = await authProxy.validate();

    if (authResponse.status === 200) {
      return NextResponse.redirect(new URL(ROUTES.HOME, request.url), { status: 307 })
    }
  }

  if (isPublicRoute) {
    return NextResponse.next();
  }

  const guard = roleGuardedPrefixes.find(
    (g) => path === g.prefix || path.startsWith(`${g.prefix}/`),
  );

  if (guard) {
    const authProxy = new AuthProxy(request);
    const authResponse = await authProxy.validate(guard.roles);

    if (authResponse.status !== 200) {
      return authResponse;
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)']
}
