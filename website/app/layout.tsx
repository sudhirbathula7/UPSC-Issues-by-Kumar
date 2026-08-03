import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "UPSC Issues by Kumar",
    template: "%s | UPSC Issues by Kumar",
  },

  description:
    "Daily editorial-based UPSC learning through curiosity questions, recall anchors, knowledge points, mains perspectives and active recall.",

  keywords: [
    "UPSC",
    "current affairs",
    "editorial analysis",
    "UPSC mains",
    "active recall",
    "UPSC Issues by Kumar",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
    >
      <body>{children}</body>
    </html>
  );
}