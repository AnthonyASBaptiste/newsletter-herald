'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Stack,
  InputAdornment,
  Card,
  CardContent,
  Breadcrumbs
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SearchIcon from '@mui/icons-material/Search';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import PauseCircleOutlineIcon from '@mui/icons-material/PauseCircleOutline';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HomeIcon from '@mui/icons-material/Home';
import Link from 'next/link';
import { useUser, useClerk } from "@clerk/nextjs";

interface Subscriber {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string | null;
}

interface Stats {
  total: number;
  active: number;
  inactive: number;
}

export default function SubscribersPage() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <SubscribersPageContent />
    </React.Suspense>
  );
}

function SubscribersPageContent() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      window.location.href = '/';
    }
  }, [isLoaded, isSignedIn]);

  if (!isLoaded || !isSignedIn) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;
  }

  const userEmail = user?.primaryEmailAddress?.emailAddress;

  // Admin Email Whitelist check
  const ADMIN_WHITELIST = ['sallto.newsletter@gmail.com', 'anthony.as.baptiste@gmail.com'];
  const hasAdminAccess = userEmail && ADMIN_WHITELIST.includes(userEmail);

  if (!hasAdminAccess) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f7', p: 3 }}>
        <Paper sx={{ p: 5, maxWidth: 500, width: '100%', textAlign: 'center', borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <Box sx={{ width: 64, height: 64, bgcolor: '#fce8e6', color: '#d93025', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
            <PeopleIcon sx={{ fontSize: 32 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, letterSpacing: '-0.01em', color: '#1d1d1f' }}>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
            Your account (<strong>{userEmail}</strong>) is not authorized to access subscriber management.
          </Typography>
          <Stack spacing={2} direction="row" justifyContent="center">
            <Button 
              variant="outlined" 
              onClick={() => signOut()} 
              sx={{ borderRadius: '980px', textTransform: 'none', px: 3 }}
            >
              Sign Out
            </Button>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button 
                variant="contained" 
                sx={{ borderRadius: '980px', textTransform: 'none', px: 3, bgcolor: '#0071e3', '&:hover': { bgcolor: '#0077ed' } }}
              >
                Go to Dashboard
              </Button>
            </Link>
          </Stack>
        </Paper>
      </Box>
    );
  }

  const [stats, setStats] = useState<Stats>({ total: 0, active: 0, inactive: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState<string>('');

  // Single Add Form States
  const [newEmail, setNewEmail] = useState<string>('');
  const [newFirstName, setNewFirstName] = useState<string>('');
  const [newLastName, setNewLastName] = useState<string>('');
  const [newPhone, setNewPhone] = useState<string>('');
  const [addLoading, setAddLoading] = useState<boolean>(false);
  const [addSuccess, setAddSuccess] = useState<string | null>(null);

  // Batch Import Modal State
  const [batchOpen, setBatchOpen] = useState<boolean>(false);
  const [batchRawInput, setBatchRawInput] = useState<string>('');
  const [batchLoading, setBatchLoading] = useState<boolean>(false);
  const [batchResult, setBatchResult] = useState<{ message: string; added: number; reactivated: number; skipped: number } | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const fetchSubscribers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${backendUrl}/subscribers`);
      if (!res.ok) throw new Error('Failed to fetch subscriber list');
      const data = await res.json();
      setSubscribers(data.subscribers || []);
      setStats(data.stats || { total: 0, active: 0, inactive: 0 });
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to load subscribers');
    } finally {
      setLoading(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    fetchSubscribers();
  }, [fetchSubscribers]);

  const handleSingleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim()) return;

    setAddLoading(true);
    setAddSuccess(null);
    setError(null);

    try {
      const res = await fetch(`${backendUrl}/subscribers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: newEmail.trim(),
          first_name: newFirstName.trim() || null,
          last_name: newLastName.trim() || null,
          phone: newPhone.trim() || null,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to add subscriber');

      setAddSuccess(data.message);
      setNewEmail('');
      setNewFirstName('');
      setNewLastName('');
      setNewPhone('');
      fetchSubscribers();
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setAddLoading(false);
    }
  };

  const handleBatchImport = async () => {
    if (!batchRawInput.trim()) return;

    setBatchLoading(true);
    setBatchResult(null);

    // Parse emails split by newline, comma, or semicolon
    const emailList = batchRawInput
      .split(/[\n,;]+/)
      .map(e => e.trim())
      .filter(e => e.length > 0);

    try {
      const res = await fetch(`${backendUrl}/subscribers/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails: emailList }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to import subscribers');

      setBatchResult(data);
      fetchSubscribers();
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setBatchLoading(false);
    }
  };

  const handleToggleActive = async (id: number, currentStatus: boolean) => {
    try {
      const res = await fetch(`${backendUrl}/subscribers/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (!res.ok) throw new Error('Failed to update status');

      // Optimistic state update
      setSubscribers(prev =>
        prev.map(sub => (sub.id === id ? { ...sub, is_active: !currentStatus } : sub))
      );
      setStats(prev => ({
        ...prev,
        active: currentStatus ? prev.active - 1 : prev.active + 1,
        inactive: currentStatus ? prev.inactive + 1 : prev.inactive - 1,
      }));
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    }
  };

  const handleDeleteSubscriber = async (id: number, email: string) => {
    if (!confirm(`Are you sure you want to remove ${email} from your subscriber list?`)) return;

    try {
      const res = await fetch(`${backendUrl}/subscribers/${id}`, {
        method: 'DELETE',
      });

      if (!res.ok) throw new Error('Failed to delete subscriber');

      fetchSubscribers();
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    }
  };

  const filteredSubscribers = subscribers.filter(s => {
    const searchLower = search.toLowerCase();
    const emailMatch = s.email.toLowerCase().includes(searchLower);
    const firstNameMatch = s.first_name ? s.first_name.toLowerCase().includes(searchLower) : false;
    const lastNameMatch = s.last_name ? s.last_name.toLowerCase().includes(searchLower) : false;
    return emailMatch || firstNameMatch || lastNameMatch;
  });

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f7', py: 5 }}>
      <Container maxWidth="lg">
        {/* Navigation Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', color: '#86868b' }}>
            <HomeIcon sx={{ mr: 0.5, fontSize: 16 }} />
            Dashboard
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}>
            <PeopleIcon sx={{ mr: 0.5, fontSize: 16, color: '#0071e3' }} />
            Subscriber Management
          </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
              Subscriber Management
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage your parish mailing list, track personal details, and view Google Contacts / website signups.
            </Typography>
          </Box>
          <Stack direction="row" spacing={2} alignItems="center">
            <Button
              variant="contained"
              startIcon={<UploadFileIcon />}
              onClick={() => { setBatchOpen(true); setBatchResult(null); setBatchRawInput(''); }}
              sx={{
                borderRadius: '980px',
                bgcolor: '#0071e3',
                py: 1.2,
                px: 3,
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: 'none',
                '&:hover': { bgcolor: '#0077ed', boxShadow: 'none' }
              }}
            >
              Batch Import Emails
            </Button>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button startIcon={<ArrowBackIcon />} variant="outlined" sx={{ borderRadius: '100px', py: 1.2, px: 3, textTransform: 'none' }}>
                Back to Dashboard
              </Button>
            </Link>
          </Stack>
        </Box>

        {/* Global Feedback Alerts */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        {addSuccess && (
          <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setAddSuccess(null)}>
            {addSuccess}
          </Alert>
        )}

        {/* Stat Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#e8f2ff', color: '#0071e3' }}>
                  <PeopleIcon fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Subscribers</Typography>
                  <Typography variant="h4" fontWeight={700}>{stats.total}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#e6f4ea', color: '#137333' }}>
                  <CheckCircleOutlineIcon fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Active Subscribers</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#137333' }}>{stats.active}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#fce8e6', color: '#c5221f' }}>
                  <PauseCircleOutlineIcon fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Unsubscribed / Paused</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#c5221f' }}>{stats.inactive}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Add Form */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Add Single Subscriber
          </Typography>
          <Box component="form" onSubmit={handleSingleAdd}>
            <Grid container spacing={2} alignItems="center">
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  placeholder="First Name"
                  fullWidth
                  value={newFirstName}
                  onChange={(e) => setNewFirstName(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  placeholder="Last Name"
                  fullWidth
                  value={newLastName}
                  onChange={(e) => setNewLastName(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  placeholder="Email (required)"
                  type="email"
                  required
                  fullWidth
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }} sx={{ display: 'flex', gap: 1.5 }}>
                <TextField
                  placeholder="Phone"
                  fullWidth
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
                <Button
                  type="submit"
                  variant="contained"
                  disabled={addLoading}
                  sx={{ borderRadius: 2, bgcolor: '#0071e3', textTransform: 'none', px: 3, minWidth: '130px' }}
                >
                  {addLoading ? <CircularProgress size={20} color="inherit" /> : 'Add'}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Paper>

        {/* Subscriber List & Search */}
        <Paper sx={{ p: 3, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Parish Subscriber List ({filteredSubscribers.length})
            </Typography>
            <TextField
              placeholder="Search subscribers by name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 320, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress color="primary" />
            </Box>
          ) : filteredSubscribers.length === 0 ? (
            <Box sx={{ textAlignment: 'center', py: 6, textAlign: 'center' }}>
              <Typography color="text.secondary">
                {search ? 'No subscribers match your search filter.' : 'No subscribers in database yet. Add your first subscriber above or import your Gmail list.'}
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#fafafa' }}>
                    <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Email Address</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Phone Number</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Date Added</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredSubscribers.map((sub) => (
                    <TableRow key={sub.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {sub.first_name || sub.last_name
                          ? `${sub.first_name || ''} ${sub.last_name || ''}`.trim()
                          : '—'}
                      </TableCell>
                      <TableCell sx={{ color: '#0071e3', fontWeight: 500 }}>{sub.email}</TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>{sub.phone || '—'}</TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>
                        {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={sub.is_active ? 'Active' : 'Unsubscribed'}
                          color={sub.is_active ? 'success' : 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end" alignItems="center">
                          <Switch
                            checked={sub.is_active}
                            onChange={() => handleToggleActive(sub.id, sub.is_active)}
                            color="success"
                            size="small"
                          />
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleDeleteSubscriber(sub.id, sub.email)}
                            title="Remove Subscriber"
                          >
                            <DeleteOutlineIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* Batch Import Dialog */}
        <Dialog open={batchOpen} onClose={() => setBatchOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>
            Import Subscribers from Gmail List or CSV
          </DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Paste your raw email list below (separated by line breaks, commas, or semicolons). Duplicates will automatically be skipped.
            </Typography>

            {batchResult && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {batchResult.message}
              </Alert>
            )}

            <TextField
              multiline
              rows={8}
              fullWidth
              placeholder={`john.doe@example.com\nmary.smith@example.com, father.paul@parish.org`}
              value={batchRawInput}
              onChange={(e) => setBatchRawInput(e.target.value)}
              disabled={batchLoading}
              sx={{ fontFamily: 'monospace' }}
            />
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 2 }}>
            <Button onClick={() => setBatchOpen(false)} disabled={batchLoading}>
              Close
            </Button>
            <Button
              variant="contained"
              onClick={handleBatchImport}
              disabled={batchLoading || !batchRawInput.trim()}
              sx={{ bgcolor: '#0071e3', textTransform: 'none', px: 3 }}
            >
              {batchLoading ? <CircularProgress size={24} color="inherit" /> : 'Import Emails'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
