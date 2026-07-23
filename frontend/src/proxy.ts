import { ROUTES } from "@/shared/constants/routes";
import { AuthProxy } from "@/shared/proxy/auth.proxy";
import { NextRequest, NextResponse } from "next/server";

const publicRoutes = ['/sign-in', '/']
const protectedRoutes = [
  '/home',
]

export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const isPublicRoute = publicRoutes.includes(path)
  const isProtectedRoute = protectedRoutes.some(route => {
    const regexPattern = '^' + route.replace(/\[.*?\]/g, '[^/]+') + '$';
    return new RegExp(regexPattern).test(path);
  });


  if(path.includes('/sign-in')) {
    const authProxy = new AuthProxy(request);
    const authResponse = await authProxy.validate();

    if (authResponse.status === 200) {
      return NextResponse.redirect(new URL(ROUTES.HOME, request.url), { status: 307 })
    }
  }

  if (isPublicRoute) {
    return NextResponse.next();
  }

  if (isProtectedRoute) {
    const authProxy = new AuthProxy(request);
    const authResponse = await authProxy.validate();

    if (authResponse.status !== 200) {
      return authResponse;
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)']
}
