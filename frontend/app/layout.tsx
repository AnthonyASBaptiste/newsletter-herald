import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppRouterCacheProvider } from '@mui/material-nextjs/v16-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from 'next/link';
import { ClerkProvider } from "@clerk/nextjs";
import AuthButtons from "./components/AuthButtons";
import React from "react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Newsletter Herald — AI-Powered Catholic Church Bulletin Summaries",
  description: "Newsletter Herald automatically parses Roman Catholic parish bulletins, extracts theological and calendar metadata, generates warm AI summaries, and schedules weekly email delivery to parishioners.",
  keywords: ["Newsletter Herald", "Catholic Church Newsletter", "Parish Bulletin Summarizer", "Liturgical AI", "Anthony Baptiste"],
  authors: [{ name: "Anthony Baptiste", url: "https://anthonybaptiste.dev" }],
  creator: "Anthony Baptiste",
  metadataBase: new URL("https://newsletter-herald.vercel.app"),
  openGraph: {
    title: "Newsletter Herald — AI-Powered Catholic Church Bulletin Summaries",
    description: "Automated bulletin processing, theological summary generation, and parishioner email scheduling.",
    url: "https://newsletter-herald.vercel.app",
    siteName: "Newsletter Herald",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Newsletter Herald",
    description: "Automated parish bulletin summarization & weekly email dispatch.",
    creator: "@anthonybaptiste",
  },
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-96x96.png', sizes: '96x96', type: 'image/png' },
      { url: '/icon.svg', type: 'image/svg+xml' },
    ],
    shortcut: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify({
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "Newsletter Herald",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "description": "Automated liturgical newsletter pipeline and Roman Catholic church bulletin summarization platform.",
                "author": {
                  "@type": "Person",
                  "name": "Anthony Baptiste",
                  "url": "https://anthonybaptiste.dev"
                },
                "creator": {
                  "@type": "Person",
                  "name": "Anthony Baptiste",
                  "url": "https://anthonybaptiste.dev"
                },
                "url": "https://newsletter-herald.vercel.app"
              })
            }}
          />
        </head>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
          <AppRouterCacheProvider>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
                <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'white', color: 'black', borderBottom: '1px solid #e0e0e0' }}>
                  <Container maxWidth="lg">
                    <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 0, sm: 2 } }}>
                      <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="h6" component="div" sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
                            HERALD
                          </Typography>
                        </Box>
                      </Link>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <React.Suspense fallback={<Box sx={{ width: 100 }} />}>
                          <AuthButtons />
                        </React.Suspense>
                      </Box>
                    </Toolbar>
                  </Container>
                </AppBar>
                <main style={{ flexGrow: 1 }}>
                  {children}
                </main>
                <Box component="footer" sx={{ py: 6, bgcolor: 'white', mt: 'auto', borderTop: '1px solid #e0e0e0' }}>
                  <Container maxWidth="lg">
                    <Typography variant="body2" color="text.secondary" align="center">
                      © {new Date().getFullYear()} Newsletter Herald. Built with ❤️ by{' '}
                      <a 
                        href="https://anthonybaptiste.dev" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={{ color: '#0071e3', textDecoration: 'none', fontWeight: 600 }}
                      >
                        Anthony
                      </a>{' '}
                      for our community.
                    </Typography>
                  </Container>
                </Box>
              </Box>
            </ThemeProvider>
          </AppRouterCacheProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
