'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Stack,
  Divider,
  Breadcrumbs,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import HomeIcon from '@mui/icons-material/Home';
import EditIcon from '@mui/icons-material/Edit';
import HistoryIcon from '@mui/icons-material/History';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useUser, useClerk } from "@clerk/nextjs";
import Link from 'next/link';

interface ErrorNewsletter {
  id: number;
  filename: string;
  drive_link?: string;
  target_sunday?: string;
  title?: string;
  summary?: string;
  status: string;
}

interface UploadLog {
  id: number;
  filename?: string;
  uploader?: string;
  status: string;
  created_at: string;
  error_message?: string;
  drive_link?: string;
}

export default function SystemErrorsPage() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <SystemErrorsPageContent />
    </React.Suspense>
  );
}

function SystemErrorsPageContent() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();

  const userEmail = user?.primaryEmailAddress?.emailAddress;

  // Admin Email Whitelist check
  const ADMIN_WHITELIST = ['sallto.newsletter@gmail.com', 'anthony.as.baptiste@gmail.com'];
  const hasAdminAccess = userEmail ? ADMIN_WHITELIST.includes(userEmail) : false;

  const [activeTab, setActiveTab] = useState(0);
  const [errorLogs, setErrorLogs] = useState<ErrorNewsletter[]>([]);
  const [uploadLogs, setUploadLogs] = useState<UploadLog[]>([]);
  const [loadingNewsletters, setLoadingNewsletters] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  // Edit Modal States
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ErrorNewsletter | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editSummary, setEditSummary] = useState('');
  const [editDate, setEditDate] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);
  const [savingArchive, setSavingArchive] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const fetchErrorNewsletters = useCallback(async () => {
    setLoadingNewsletters(true);
    try {
      const response = await fetch(`${backendUrl}/newsletters`);
      if (response.ok) {
        const data = await response.json();
        const failures = (data.newsletters || []).filter((n: ErrorNewsletter) => n.status === 'failed_validation');
        setErrorLogs(failures);
      }
    } catch (err) {
      console.error("Failed to fetch newsletters:", err);
    } finally {
      setLoadingNewsletters(false);
    }
  }, [backendUrl]);

  const fetchUploadLogs = useCallback(async () => {
    setLoadingLogs(true);
    try {
      const response = await fetch(`${backendUrl}/upload-logs`, {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUploadLogs(data.upload_logs || []);
      }
    } catch (err) {
      console.error("Failed to fetch upload logs:", err);
    } finally {
      setLoadingLogs(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      window.location.href = '/';
    }
  }, [isLoaded, isSignedIn]);

  useEffect(() => {
    if (user && hasAdminAccess) {
      fetchErrorNewsletters();
      fetchUploadLogs();
    }
  }, [user, hasAdminAccess, fetchErrorNewsletters, fetchUploadLogs]);

  if (!isLoaded || !isSignedIn) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;
  }

  if (!hasAdminAccess) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f7', p: 3 }}>
        <Paper sx={{ p: 5, maxWidth: 500, width: '100%', textAlign: 'center', borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <Box sx={{ width: 64, height: 64, bgcolor: '#fce8e6', color: '#d93025', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
            <ErrorOutlineIcon sx={{ fontSize: 32 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, letterSpacing: '-0.01em', color: '#1d1d1f' }}>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
            Your account (<strong>{userEmail}</strong>) is not authorized to access system error logs.
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

  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/approve`);
      if (res.ok) {
        setMessage("Newsletter approved and scheduled successfully!");
        fetchErrorNewsletters();
      } else {
        alert("Failed to approve newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (id: number) => {
    if (!confirm("Are you sure you want to archive this validation failure?")) return;
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({ status: 'superseded' }),
      });
      if (res.ok) {
        setMessage("Newsletter archived successfully.");
        fetchErrorNewsletters();
      } else {
        alert("Failed to archive newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (item: ErrorNewsletter) => {
    setEditingItem(item);
    setEditTitle(item.title || '');
    setEditSummary(item.summary || '');
    setEditDate(item.target_sunday ? item.target_sunday.split('T')[0] : '');
    setEditModalOpen(true);
  };

  const handleSaveAndApprove = async () => {
    if (!editingItem) return;
    setSavingEdit(true);
    try {
      // 1. Update the target Sunday, title, and summary
      const response = await fetch(`${backendUrl}/newsletters/${editingItem.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({
          title: editTitle,
          summary: editSummary,
          target_sunday: editDate || null,
          status: 'draft' // Revert to draft first to enable approval
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update details");
      }

      // 2. Approve/schedule it
      const approveRes = await fetch(`${backendUrl}/newsletters/${editingItem.id}/approve`);
      if (approveRes.ok) {
        setMessage(`Successfully corrected details and approved "${editTitle}"!`);
        setEditModalOpen(false);
        fetchErrorNewsletters();
      } else {
        alert("Saved details, but failed to approve automatically.");
      }
    } catch (err) {
      const error = err as Error;
      alert(`Error updating newsletter: ${error.message}`);
    } finally {
      setSavingEdit(false);
    }
  };

  const handleSaveArchiveOnly = async () => {
    if (!editingItem) return;
    setSavingArchive(true);
    try {
      // Update details and set status directly to 'delivered' and delivered to true
      const response = await fetch(`${backendUrl}/newsletters/${editingItem.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({
          title: editTitle,
          summary: editSummary,
          target_sunday: editDate || null,
          status: 'delivered',
          delivered: true
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to archive details");
      }

      setMessage(`Successfully archived "${editTitle}" directly without scheduling!`);
      setEditModalOpen(false);
      fetchErrorNewsletters();
    } catch (err) {
      const error = err as Error;
      alert(`Error archiving newsletter: ${error.message}`);
    } finally {
      setSavingArchive(false);
    }
  };

  return (
    <Box sx={{ minHeight: '90vh', bgcolor: '#f5f5f7', py: 6 }}>
      <Container maxWidth="lg">
        {/* Navigation Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', color: '#86868b' }}>
            <HomeIcon sx={{ mr: 0.5, fontSize: 16 }} />
            Dashboard
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}>
            <WarningIcon sx={{ mr: 0.5, fontSize: 16, color: '#d93025' }} />
            System Errors & Ingest Logs
          </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
              System Ingestion & Errors
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Monitor batch and manual document uploads, and rectify target-date mismatch validation failures.
            </Typography>
          </Box>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <Button startIcon={<ArrowBackIcon />} variant="outlined" sx={{ borderRadius: '100px', textTransform: 'none' }}>
              Back to Dashboard
            </Button>
          </Link>
        </Box>

        {message && (
          <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setMessage(null)}>
            {message}
          </Alert>
        )}

        {/* Tab System */}
        <Paper sx={{ borderRadius: 3, mb: 4, overflow: 'hidden', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
          <Tabs
            value={activeTab}
            onChange={(_, val) => setActiveTab(val)}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
            sx={{ borderBottom: '1px solid #e0e0e0', bgcolor: 'white' }}
          >
            <Tab 
              icon={<WarningIcon sx={{ fontSize: 18 }} />} 
              iconPosition="start" 
              label={`Validation Failures (${errorLogs.length})`} 
              sx={{ textTransform: 'none', fontWeight: 700, minHeight: 60 }} 
            />
            <Tab 
              icon={<HistoryIcon sx={{ fontSize: 18 }} />} 
              iconPosition="start" 
              label={`Ingestion/Upload Logs (${uploadLogs.length})`} 
              sx={{ textTransform: 'none', fontWeight: 700, minHeight: 60 }} 
            />
          </Tabs>
        </Paper>

        {/* Tab Panel: Validation Failures */}
        {activeTab === 0 && (
          loadingNewsletters ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : errorLogs.length === 0 ? (
            <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
              <CheckCircleIcon sx={{ fontSize: 60, color: '#137333', mb: 2 }} />
              <Typography variant="h6" fontWeight={700}>
                No Validation Failures
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                All ingested bulletins matched the schedule target Sunday successfully.
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={3}>
              {errorLogs.map((item) => (
                <Grid size={{ xs: 12, md: 6 }} key={item.id}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)', border: '1px solid #fce8e6', bgcolor: '#fdf7f7', height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="subtitle1" fontWeight={700} color="error" sx={{ wordBreak: 'break-all', mr: 2 }}>
                          {item.filename}
                        </Typography>
                        {item.drive_link && (
                          <IconButton size="small" href={item.drive_link} target="_blank" title="View File">
                            <OpenInNewIcon fontSize="small" />
                          </IconButton>
                        )}
                      </Box>
                      <Divider sx={{ my: 1.5, borderColor: '#fce8e6' }} />
                      
                      <Box sx={{ mb: 3, flexGrow: 1 }}>
                        <Typography variant="body2" sx={{ color: '#d93025', fontWeight: 700, mb: 1 }}>
                          ⚠️ Target Date Mismatch
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#5f6368', lineHeight: 1.6 }}>
                          The extracted target Sunday is <strong>{item.target_sunday ? new Date(item.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' }) : 'Unknown'}</strong>, which does not match the expected next Sunday. This usually happens when uploading older historical newsletters or if the file content dates are scanned/unreadable.
                        </Typography>
                      </Box>

                      <Stack direction="row" spacing={1.5} flexWrap="wrap" gap={1} sx={{ mt: 'auto' }}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => openEditModal(item)}
                          sx={{ textTransform: 'none', borderRadius: 2, boxShadow: 'none', '&:hover': { boxShadow: 'none' } }}
                        >
                          Edit & Approve
                        </Button>
                        <Button
                          variant="outlined"
                          color="success"
                          size="small"
                          startIcon={<CheckCircleIcon />}
                          onClick={() => handleApprove(item.id)}
                          sx={{ textTransform: 'none', borderRadius: 2 }}
                        >
                          Approve Anyway
                        </Button>
                        <Button
                          variant="outlined"
                          color="error"
                          size="small"
                          startIcon={<CancelIcon />}
                          onClick={() => handleReject(item.id)}
                          sx={{ textTransform: 'none', borderRadius: 2 }}
                        >
                          Archive
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )
        )}

        {/* Tab Panel: Ingestion/Upload Logs */}
        {activeTab === 1 && (
          loadingLogs ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : uploadLogs.length === 0 ? (
            <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
              <HistoryIcon sx={{ fontSize: 60, color: '#86868b', mb: 2 }} />
              <Typography variant="h6" fontWeight={700}>
                No Upload Logs Available
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Logs will populate as documents are uploaded manually or via batch processes.
              </Typography>
            </Paper>
          ) : (
            <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', overflow: 'hidden' }}>
              <Table>
                <TableHead sx={{ bgcolor: '#f5f5f7' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Filename</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Uploader</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Time</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Error Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {uploadLogs.map((log) => (
                    <TableRow key={log.id} hover>
                      <TableCell sx={{ fontWeight: 600, wordBreak: 'break-all', maxWidth: 300 }}>{log.filename}</TableCell>
                      <TableCell>
                        <Chip 
                          label={log.uploader} 
                          size="small" 
                          variant="outlined" 
                          color={log.uploader === 'local_batch_upload' ? 'secondary' : 'default'}
                        />
                      </TableCell>
                      <TableCell sx={{ whiteSpace: 'nowrap' }}>
                        {log.created_at ? new Date(log.created_at).toLocaleString() : ''}
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={log.status === 'success' ? <CheckCircleIcon /> : <ErrorOutlineIcon />}
                          label={log.status.toUpperCase()}
                          color={log.status === 'success' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#d93025', fontSize: '0.85rem', maxWidth: 400, wordBreak: 'break-word' }}>
                        {log.error_message || '—'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )
        )}
      </Container>

      {/* Edit Date & Details Dialog Modal */}
      <Dialog open={editModalOpen} onClose={() => setEditModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          Edit & Approve Validation Failure
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Manually correct the schedule target Sunday and details extracted by AI. Saving will override validation and publish the newsletter on the selected Sunday.
          </Typography>

          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Target Sunday (Schedule Date)"
              type="date"
              fullWidth
              value={editDate}
              onChange={(e) => setEditDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              helperText="The specific Sunday liturgical date for this newsletter bulletin issue."
            />
            <TextField
              label="Liturgical Title"
              fullWidth
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="e.g. 1st Sunday of Advent"
            />
            <TextField
              label="Weekly Summary Narrative"
              fullWidth
              multiline
              rows={5}
              value={editSummary}
              onChange={(e) => setEditSummary(e.target.value)}
              placeholder="Enter the 2-paragraph highlight summary for parishioners..."
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
          <Button onClick={() => setEditModalOpen(false)} color="inherit" sx={{ borderRadius: '100px', textTransform: 'none' }}>
            Cancel
          </Button>
          <Stack direction="row" spacing={2}>
            <Button
              onClick={handleSaveArchiveOnly}
              variant="outlined"
              color="primary"
              disabled={savingEdit || savingArchive || !editDate}
              sx={{ borderRadius: '100px', textTransform: 'none' }}
            >
              {savingArchive ? <CircularProgress size={20} color="inherit" /> : 'Archive Only (No Email)'}
            </Button>
            <Button
              onClick={handleSaveAndApprove}
              variant="contained"
              color="primary"
              disabled={savingEdit || savingArchive || !editDate}
              sx={{ borderRadius: '100px', textTransform: 'none', px: 4 }}
            >
              {savingEdit ? <CircularProgress size={20} color="inherit" /> : 'Save & Schedule Email'}
            </Button>
          </Stack>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
