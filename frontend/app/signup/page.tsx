'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Stack,
  Card,
  CardContent
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import Link from 'next/link';

export default function PublicSignupPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setSuccess(null);
    setError(null);

    try {
      const res = await fetch(`${backendUrl}/subscribers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to sign up');

      setSuccess(data.message || 'Successfully subscribed!');
      setEmail('');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to complete signup';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      minHeight: '80vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      bgcolor: '#f5f5f7',
      py: 6,
      px: 2
    }}>
      <Container maxWidth="sm">
        <Link href="/" style={{ textDecoration: 'none' }}>
          <Button startIcon={<ArrowBackIcon />} variant="outlined" sx={{ borderRadius: '100px', mb: 3, textTransform: 'none' }}>
            Back to Home
          </Button>
        </Link>


        <Card sx={{ borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)', border: '1px solid #e0e0e0', overflow: 'hidden' }}>
          <Box sx={{ bgcolor: '#0071e3', py: 4, textAlign: 'center', color: 'white' }}>
            <MarkEmailReadIcon sx={{ fontSize: 50, mb: 1 }} />
            <Typography variant="h5" fontWeight={700}>
              Join Our Parish Mailing List
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Receive weekly bulletins and announcements straight to your inbox.
            </Typography>
          </Box>

          <CardContent sx={{ p: 4 }}>
            {success ? (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                  {success}
                </Alert>
                <Typography variant="body1" sx={{ color: '#515154', mb: 3 }}>
                  Thank you for subscribing! You will receive our next newsletter issue on Sunday morning.
                </Typography>
                <Link href="/" style={{ textDecoration: 'none' }}>
                  <Button variant="contained" sx={{ borderRadius: '100px', px: 4, bgcolor: '#0071e3' }}>
                    Go to Home
                  </Button>
                </Link>
              </Box>
            ) : (
              <Box component="form" onSubmit={handleSignup}>
                {error && (
                  <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
                    {error}
                  </Alert>
                )}

                <Stack spacing={3}>
                  <Typography variant="body2" color="text.secondary">
                    Please enter your email address below to subscribe to the weekly parish newsletter.
                  </Typography>

                  <TextField
                    label="Email Address"
                    type="email"
                    fullWidth
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    disabled={loading}
                    size="large"
                    sx={{ 
                      borderRadius: '980px', 
                      py: 1.5, 
                      bgcolor: '#0071e3', 
                      textTransform: 'none', 
                      fontWeight: 600,
                      boxShadow: 'none',
                      '&:hover': { bgcolor: '#0077ed', boxShadow: 'none' }
                    }}
                  >
                    {loading ? <CircularProgress size={24} color="inherit" /> : 'Subscribe to Newsletter'}
                  </Button>
                </Stack>
              </Box>
            )}
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}
