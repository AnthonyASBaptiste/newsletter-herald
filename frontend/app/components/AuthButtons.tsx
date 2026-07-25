'use client';

import { Box, Button } from "@mui/material";
import { useUser, UserButton, SignInButton } from "@clerk/nextjs";
import Link from "next/link";

export default function AuthButtons() {
  const { isLoaded, isSignedIn } = useUser();

  if (!isLoaded) {
    return <Box sx={{ width: 100 }} />;
  }

  return (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
      {isSignedIn ? (
        <UserButton />
      ) : (
        <>
          <SignInButton mode="modal" fallbackRedirectUrl="/">
            <Button variant="text" color="primary" sx={{ textTransform: 'none', fontWeight: 600 }}>
              Login
            </Button>
          </SignInButton>
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <Button 
              variant="contained" 
              color="primary" 
              sx={{ px: 3, borderRadius: '980px', textTransform: 'none', fontWeight: 600 }} 
            >
              Join Mailing List
            </Button>
          </Link>
        </>
      )}
    </Box>
  );
}
