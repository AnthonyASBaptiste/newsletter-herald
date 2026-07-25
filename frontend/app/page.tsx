'use client';

import React from 'react';
import { Box, CircularProgress } from '@mui/material';
import { useSearchParams } from 'next/navigation';
import { HomeContent } from "./HomeContent";

function HomeWithSearchParams() {
  const searchParams = useSearchParams();
  const forcePublic = searchParams.get('forcePublic') === 'true';
  return <HomeContent forcePublic={forcePublic} />;
}

export default function Home() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <HomeWithSearchParams />
    </React.Suspense>
  );
}
