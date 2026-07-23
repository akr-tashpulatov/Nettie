import "./globals.css";
import { Inter } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { QueryProvider } from "./providers";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/shared/session/auth-provider";
import { TooltipProvider } from "@/shared/components/ui/tooltip";
import { getLocale } from "next-intl/server";

const inter = Inter({
  subsets: ["latin", "cyrillic", "cyrillic-ext"],
  variable: "--font-inter",
});

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();

  return (
    <html lang={locale} className={inter.variable}>
      <body className={`antialiased`}>
        <AuthProvider>
          <NextIntlClientProvider>
            <QueryProvider>
              <TooltipProvider>
                <Toaster></Toaster>
                {children}
              </TooltipProvider>
            </QueryProvider>
          </NextIntlClientProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
