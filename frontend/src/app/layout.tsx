/**
 * Root Layout - AI Strategy Hub
 * Layout principale dell'applicazione con metadata e providers
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { cn } from '@/lib/utils';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

export const metadata: Metadata = {
  title: {
    default: 'AI Strategy Hub',
    template: '%s | AI Strategy Hub',
  },
  description:
    'Consulenza AI, GDPR e Cybersecurity. Supporto strategico per aziende che vogliono innovare in sicurezza.',
  keywords: [
    'AI',
    'GDPR',
    'Cybersecurity',
    'NIS2',
    'Consulenza',
    'Compliance',
    'Privacy',
    'Data Protection',
  ],
  authors: [{ name: 'Davide Botto', url: 'https://aistrategyhub.eu' }],
  creator: 'Davide Botto',
  publisher: 'AI Strategy Hub',
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL || 'https://aistrategyhub.eu'
  ),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'it_IT',
    url: 'https://aistrategyhub.eu',
    siteName: 'AI Strategy Hub',
    title: 'AI Strategy Hub - Consulenza AI, GDPR e Cybersecurity',
    description:
      'Supporto strategico per aziende che vogliono innovare con AI in sicurezza e compliance.',
    images: [
      {
        url: '/logo.png',
        width: 1200,
        height: 630,
        alt: 'AI Strategy Hub',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Strategy Hub',
    description:
      'Consulenza AI, GDPR e Cybersecurity per aziende che innovano in sicurezza.',
    images: ['/logo.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it" suppressHydrationWarning>
      <body
        className={cn(
          'min-h-screen bg-background font-sans antialiased',
          inter.variable
        )}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
