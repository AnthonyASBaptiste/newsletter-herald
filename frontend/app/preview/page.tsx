'use client';

import React from 'react';
import { HomeContent } from '../HomeContent';
import { Box, Button, Container, Typography } from '@mui/material';
import Link from 'next/link';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

export default function PreviewPage() {
  return (
    <Box sx={{ position: 'relative' }}>
      {/* Admin Preview Banner */}
      <Box sx={{ bgcolor: '#fff3cd', borderBottom: '1px solid #ffeeba', py: 1.5 }}>
        <Container maxWidth="lg" sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="body2" sx={{ color: '#856404', fontWeight: 600 }}>
            👀 Preview Mode: You are viewing the landing page exactly as an unauthenticated guest.
          </Typography>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <Button
              variant="outlined"
              color="warning"
              size="small"
              startIcon={<ArrowBackIcon />}
              sx={{ borderRadius: '100px', textTransform: 'none', px: 3 }}
            >
              Return to Console
            </Button>
          </Link>
        </Container>
      </Box>

      {/* Main Home Page forced to Public */}
      <HomeContent forcePublic={true} />
    </Box>
  );
}
