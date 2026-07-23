import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    dangerouslyAllowLocalIP: true,
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '9000',
        pathname: '/storage/**',
      },
    ],
  },
};

const withNextIntl = createNextIntlPlugin({ requestConfig: './src/shared/i18n/request.ts' });
export default withNextIntl(nextConfig);