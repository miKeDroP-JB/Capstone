import type { Metadata } from "next";
import { Cinzel, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const cinzel = Cinzel({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "0r8 — The Operating System for Human Potential",
  description:
    "Intelligence. Intuition. Integration. The AI that multiplies humans.",
  keywords: [
    "0r8",
    "AI",
    "operating system",
    "intelligence",
    "intuition",
    "integration",
  ],
  authors: [{ name: "0r8 Empire" }],
  openGraph: {
    title: "0r8 — The Operating System for Human Potential",
    description:
      "Intelligence. Intuition. Integration. The AI that multiplies humans.",
    url: "https://0r8.ai",
    siteName: "0r8",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "0r8 — The Operating System for Human Potential",
    description:
      "Intelligence. Intuition. Integration. The AI that multiplies humans.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${cinzel.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} font-body antialiased bg-void text-white min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}
