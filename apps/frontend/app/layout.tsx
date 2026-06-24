import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MED.MIX OS | نظام إدارة المبيعات",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
