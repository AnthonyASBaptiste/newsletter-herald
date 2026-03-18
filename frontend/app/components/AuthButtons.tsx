'use client';

import { Box, Button, Typography } from "@mui/material";
import { useUser } from "@stackframe/stack";
import Link from "next/link";

export default function AuthButtons() {
  const user = useUser();

  if (user) {
    return (
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {user.primaryEmail}
        </Typography>
        <Button 
          variant="outlined" 
          color="primary" 
          size="small"
          onClick={() => user.signOut()}
        >
          Logout
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', gap: 2 }}>
      <Link href="/handler/sign-in" style={{ textDecoration: 'none' }}>
        <Button 
          variant="text" 
          color="primary" 
        >
          Login
        </Button>
      </Link>
      <Link href="/handler/sign-up" style={{ textDecoration: 'none' }}>
        <Button 
          variant="contained" 
          color="primary" 
          sx={{ px: 3 }} 
        >
          Sign Up
        </Button>
      </Link>
    </Box>
  );
}
