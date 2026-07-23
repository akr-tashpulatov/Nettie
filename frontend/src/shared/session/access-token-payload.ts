import z from "zod";
import { Role } from "@/shared/api/generated/model/role";

export const accessTokenPayloadSchema = z.object({
  sub: z.string(),
  role: z.enum(Role),
  email: z.string(),
  full_name: z.string(),
  phone_number: z.string().nullish(),
  type: z.literal("access"),
  jti: z.string(),
  iat: z.number(),
  exp: z.number(),
});

export type AccessTokenPayload = z.infer<typeof accessTokenPayloadSchema>;

export const decodeAccessToken = (token: string): AccessTokenPayload | null => {
  const segment = token.split(".")[1];
  if (!segment) return null;
  try {
    const base64 = segment.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
    const json = new TextDecoder().decode(
      Uint8Array.from(atob(padded), (c) => c.charCodeAt(0)),
    );
    const result = accessTokenPayloadSchema.safeParse(JSON.parse(json));
    return result.success ? result.data : null;
  } catch {
    return null;
  }
};

export const isAccessTokenExpired = (payload: AccessTokenPayload): boolean =>
  payload.exp * 1000 <= Date.now();
