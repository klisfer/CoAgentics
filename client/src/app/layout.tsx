import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CoAgentics AI Finance",
  description: "AI-powered financial assistant and planning platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
