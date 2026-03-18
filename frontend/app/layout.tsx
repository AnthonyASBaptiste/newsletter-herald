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
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Link from 'next/link';
import { StackProvider, StackTheme } from "@stackframe/stack";
import { stackClientApp } from "../stack/client";
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
  title: "Herald - Church Newsletter Summaries",
  description: "Summarize Roman Catholic church newsletters with ease.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <StackProvider app={stackClientApp}>
          <StackTheme>
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
                          <Link href="#" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <Button color="inherit" sx={{ fontWeight: 500 }}>About</Button>
                          </Link>
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
                        © {new Date().getFullYear()} SALLTO Herald. Built with ❤️ for our community.
                      </Typography>
                    </Container>
                  </Box>
                </Box>
              </ThemeProvider>
            </AppRouterCacheProvider>
          </StackTheme>
        </StackProvider>
      </body>
    </html>
  );
}
