import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

import { ROUTES } from "@/shared/constants/routes";
import { Role } from "@/shared/api/generated/model/role";
import {
  AccessTokenPayload,
  decodeAccessToken,
} from "@/shared/session/access-token-payload";

const ACCESS_TOKEN_COOKIE = "access_token";
const REFRESH_TOKEN_COOKIE = "refresh_token";

export class AuthProxy {
  private readonly request: NextRequest;

  constructor(request: NextRequest) {
    this.request = request;
  }

  private redirectToSignIn(): NextResponse {
    const url = this.request.nextUrl.clone()
    url.pathname = "/sign-in"
    url.search = `?redirect=${this.request.nextUrl.pathname}`
    return NextResponse.redirect(url, { status: 307 })
  }

  async getAccessTokenPayload(): Promise<AccessTokenPayload | null> {
    const cookieStore = await cookies();
    const token = cookieStore.get(ACCESS_TOKEN_COOKIE)?.value;
    return token ? decodeAccessToken(token) : null;
  }

  async validate(requiredRoles?: Role[]): Promise<NextResponse> {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE);
    const refreshToken = cookieStore.get(REFRESH_TOKEN_COOKIE);

    if (!accessToken && !refreshToken) {
      return this.redirectToSignIn();
    }

    if (requiredRoles?.length) {
      const payload = accessToken ? decodeAccessToken(accessToken.value) : null;
      if (payload && !requiredRoles.includes(payload.role)) {
        return NextResponse.redirect(new URL(ROUTES.HOME, this.request.url), {
          status: 307,
        });
      }
    }

    return NextResponse.next();
  }
}
