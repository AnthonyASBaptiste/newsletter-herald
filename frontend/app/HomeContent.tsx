'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Paper, 
  Grid, 
  CircularProgress,
  Fade,
  Alert,
  Stack,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  TextField,
  Divider,
  Switch,
  FormControlLabel
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import CloseIcon from '@mui/icons-material/Close';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningIcon from '@mui/icons-material/Warning';
import DownloadIcon from '@mui/icons-material/Download';
import PeopleIcon from '@mui/icons-material/People';
import ScheduleIcon from '@mui/icons-material/Schedule';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import EditIcon from '@mui/icons-material/Edit';
import { useUser, useClerk } from "@clerk/nextjs";
import Link from "next/link";

interface Newsletter {
  id: number;
  filename?: string;
  drive_link?: string;
  target_sunday?: string;
  uploaded_at?: string;
  title?: string;
  summary?: string;
  status: string;
  tags?: string;
  thumbnail_id?: string;
  scheduled_at?: string;
}

interface SummaryResponse {
  newsletter_id?: number;
  schedule_date?: string;
  liturgical_season?: string;
  calendar_year?: number;
  title?: string;
  summary?: string;
}



export function HomeContent({ forcePublic = false }: { forcePublic?: boolean }) {
  const { isSignedIn, user: clerkUser } = useUser();
  const { signOut } = useClerk();
  
  const user = (forcePublic || !isSignedIn) ? null : clerkUser;
  const userEmail = clerkUser?.primaryEmailAddress?.emailAddress;

  // Admin Email Whitelist check
  const ADMIN_WHITELIST = ['sallto.newsletter@gmail.com', 'anthony.as.baptiste@gmail.com'];
  const hasAdminAccess = !user || (userEmail && ADMIN_WHITELIST.includes(userEmail));

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [, setSummary] = useState<SummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [publicNewsletters, setPublicNewsletters] = useState<Newsletter[]>([]);
  const [fetchingNewsletters, setFetchingNewsletters] = useState(false);
  const [subscribersCount, setSubscribersCount] = useState(0);

  // New state for confirmation and editing
  const [, setScheduleDate] = useState("");
  const [, setTags] = useState("");
  
  // Modal state for viewing summaries
  const [selectedNewsletter, setSelectedNewsletter] = useState<Newsletter | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Upload Modal State
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [evalDemoMode, setEvalDemoMode] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  // Edit Schedule Modal State
  const [editScheduledOpen, setEditScheduledOpen] = useState(false);
  const [editScheduledTitle, setEditScheduledTitle] = useState("");
  const [editScheduledSummary, setEditScheduledSummary] = useState("");
  const [editScheduledDate, setEditScheduledDate] = useState("");
  const [editScheduledTime, setEditScheduledTime] = useState("");
  const [editScheduledSaving, setEditScheduledSaving] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const fetchNewsletters = useCallback(async () => {
    setFetchingNewsletters(true);
    try {
      const response = await fetch(`${backendUrl}/newsletters`);
      if (response.ok) {
        const data = await response.json();
        setPublicNewsletters(data.newsletters || []);
      }
    } catch (err) {
      console.error("Failed to fetch newsletters:", err);
    } finally {
      setFetchingNewsletters(false);
    }
  }, [backendUrl]);

  const fetchSubscribersCount = useCallback(async () => {
    try {
      const res = await fetch(`${backendUrl}/subscribers`);
      if (res.ok) {
        const data = await res.json();
        setSubscribersCount(data.stats?.active || 0);
      }
    } catch (err) {
      console.error("Failed to fetch subscribers stats:", err);
    }
  }, [backendUrl]);

  useEffect(() => {
    fetchNewsletters();
    if (user) {
      fetchSubscribersCount();
    }
  }, [user, fetchNewsletters, fetchSubscribersCount]);

  if (user && !hasAdminAccess) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f7', p: 3 }}>
        <Paper sx={{ p: 5, maxWidth: 500, width: '100%', textAlign: 'center', borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <Box sx={{ width: 64, height: 64, bgcolor: '#fce8e6', color: '#d93025', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
            <WarningIcon sx={{ fontSize: 32 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, letterSpacing: '-0.01em', color: '#1d1d1f' }}>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
            Your account (<strong>{userEmail}</strong>) is not authorized as an administrator for Newsletter Herald.
          </Typography>
          <Stack spacing={2} direction="row" justifyContent="center">
            <Button 
              variant="outlined" 
              onClick={() => signOut()} 
              sx={{ borderRadius: '980px', textTransform: 'none', px: 3 }}
            >
              Sign Out
            </Button>
            <Link href="/?forcePublic=true" style={{ textDecoration: 'none' }}>
              <Button 
                variant="contained" 
                sx={{ borderRadius: '980px', textTransform: 'none', px: 3, bgcolor: '#0071e3', '&:hover': { bgcolor: '#0077ed' } }}
              >
                View Public Feed
              </Button>
            </Link>
          </Stack>
        </Paper>
      </Box>
    );
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError(null);
    setSummary(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${backendUrl}/upload-document`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630', 
          'X-User-Email': userEmail || 'anonymous',
          'X-Demo-Mode': evalDemoMode ? 'true' : 'false',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      const data = await response.json();
      setSummary(data.summary);
      
      // Initialize edit fields from AI response
      setScheduleDate(data.summary.schedule_date || '');
      
      // Construct initial tags from liturgical info
      const tagsList = [];
      if (data.summary.liturgical_season) tagsList.push(data.summary.liturgical_season.toLowerCase().replace(" ", "-"));
      if (data.summary.calendar_year) tagsList.push(String(data.summary.calendar_year));
      
      setTags(tagsList.join(', '));
      setUploadModalOpen(false); // Close modal on success
      setFile(null); // Clear selected file

      if (data.summary?.demo_mode) {
        alert(`🧪 [DEMO / PREVIEW MODE ACTIVE]\n\nNewsletter uploaded & immediate preview email sent!\nRecipient: ${data.summary.demo_recipient || userEmail || 'your email'}\nSubject: [DEMO/PREVIEW] ${data.summary.title}`);
      }
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSchedule = async (id: number) => {
    if (!confirm("Are you sure you want to cancel the scheduled delivery? The newsletter will revert to draft status.")) return;
    try {
      const response = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({ status: 'draft' }),
      });
      if (response.ok) {
        alert("Delivery canceled. Newsletter reverted to drafts.");
        fetchNewsletters();
      } else {
        alert("Failed to cancel schedule.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/approve`);
      if (res.ok) {
        alert("Newsletter approved and scheduled for Sunday morning!");
        fetchNewsletters();
      } else {
        alert("Failed to approve newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRegenerate = async (id: number) => {
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/regenerate`);
      if (res.ok) {
        alert("AI summary regenerated successfully!");
        fetchNewsletters();
      } else {
        alert("Failed to regenerate summary.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (id: number) => {
    if (!confirm("Are you sure you want to reject and supersede this newsletter summary?")) return;
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
        fetchNewsletters();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenEditScheduled = (newsletter: Newsletter) => {
    setEditScheduledTitle(newsletter.title || "");
    setEditScheduledSummary(newsletter.summary || "");
    
    // Parse scheduled_at if set, otherwise default to target_sunday at 08:00
    if (newsletter.scheduled_at) {
      try {
        const dt = new Date(newsletter.scheduled_at);
        const year = dt.getFullYear();
        const month = String(dt.getMonth() + 1).padStart(2, '0');
        const date = String(dt.getDate()).padStart(2, '0');
        const hours = String(dt.getHours()).padStart(2, '0');
        const minutes = String(dt.getMinutes()).padStart(2, '0');
        
        setEditScheduledDate(`${year}-${month}-${date}`);
        setEditScheduledTime(`${hours}:${minutes}`);
      } catch (e) {
        console.error("Failed to parse scheduled_at date", e);
        setEditScheduledDate(newsletter.target_sunday || "");
        setEditScheduledTime("08:00");
      }
    } else if (newsletter.target_sunday) {
      setEditScheduledDate(newsletter.target_sunday);
      setEditScheduledTime("08:00");
    } else {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const date = String(today.getDate()).padStart(2, '0');
      setEditScheduledDate(`${year}-${month}-${date}`);
      setEditScheduledTime("08:00");
    }
    setEditScheduledOpen(true);
  };

  const handleSaveScheduledChanges = async (id: number) => {
    if (!editScheduledDate || !editScheduledTime) {
      alert("Please select both a date and a time for scheduling.");
      return;
    }
    setEditScheduledSaving(true);
    try {
      const scheduledAtStr = `${editScheduledDate}T${editScheduledTime}:00`;
      
      const response = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({
          title: editScheduledTitle,
          summary: editScheduledSummary,
          scheduled_at: scheduledAtStr,
          target_sunday: editScheduledDate
        }),
      });
      if (response.ok) {
        alert("Newsletter schedule and content updated successfully!");
        setEditScheduledOpen(false);
        fetchNewsletters();
      } else {
        alert("Failed to save changes.");
      }
    } catch (err) {
      console.error(err);
      alert("Error saving changes.");
    } finally {
      setEditScheduledSaving(false);
    }
  };

  // Filter lists for dashboard
  const pendingApprovals = publicNewsletters.filter(n => n.status === 'draft');
  const errorLogs = publicNewsletters.filter(n => n.status === 'failed_validation');
  
  // Find latest scheduled newsletter
  const scheduledNewsletters = publicNewsletters.filter(n => n.status === 'scheduled');
  const latestScheduled = scheduledNewsletters.length > 0 ? scheduledNewsletters[0] : null;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f7' }}>
      
      {/* 1. PUBLIC HERO SECTION (Only visible if NOT logged in) */}
      {!user && (
        <Box 
          sx={{ 
            pt: { xs: 8, md: 12 }, 
            pb: { xs: 8, md: 10 }, 
            bgcolor: 'white',
            borderBottom: '1px solid #e0e0e0',
            textAlign: 'center'
          }}
        >
          <Container maxWidth="md">
            <Fade in timeout={800}>
              <Box>
                <Typography 
                  variant="h1" 
                  sx={{ 
                    fontSize: { xs: '2.5rem', md: '4rem' }, 
                    mb: 2,
                    letterSpacing: '-0.04em',
                    fontWeight: 800
                  }}
                >
                  Stay Connected with <br /> 
                  <Box component="span" sx={{ color: '#0071e3' }}>Your Parish.</Box>
                </Typography>
                <Typography 
                  variant="h6" 
                  color="text.secondary" 
                  sx={{ mb: 6, fontWeight: 400, maxWidth: '600px', mx: 'auto' }}
                >
                  Read the latest church newsletters and stay up to date with 
                  community events, prayers, and announcements.
                </Typography>
              </Box>
            </Fade>

            <Box sx={{ maxWidth: '600px', mx: 'auto' }}>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
                <Link href="/signup" style={{ textDecoration: 'none' }}>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    size="large"
                    sx={{ 
                      borderRadius: '100px', 
                      px: 6, 
                      py: 2, 
                      fontSize: '1.1rem', 
                      width: { xs: '100%', sm: 'auto' },
                      textTransform: 'none',
                      boxShadow: 'none',
                      '&:hover': { boxShadow: 'none' }
                    }}
                  >
                    Join Mailing List
                  </Button>
                </Link>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  size="large"
                  sx={{ borderRadius: '100px', px: 6, py: 2, fontSize: '1.1rem', width: { xs: '100%', sm: 'auto' }, textTransform: 'none' }}
                  onClick={() => document.getElementById('newsletters-feed')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  Browse Newsletters
                </Button>
              </Stack>
            </Box>
          </Container>
        </Box>
      )}

      {/* 2. AUTHENTICATED CONSOLE HEADER (Only visible if logged in) */}
      {user && (
        <Box sx={{ pt: 5, pb: 2, bgcolor: 'white', borderBottom: '1px solid #e0e0e0' }}>
          <Container maxWidth="lg">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
                  Console Dashboard
                </Typography>
                <Typography variant="body1" sx={{ color: '#86868b' }}>
                  Welcome back, {userEmail}. Manage parish newsletters, approvals, and error states.
                </Typography>
              </Box>
              
              <Stack direction="row" spacing={2} alignItems="center">
                <Paper
                  variant="outlined"
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    px: 2,
                    py: 0.5,
                    borderRadius: '980px',
                    borderColor: evalDemoMode ? '#ffa726' : '#e0e0e0',
                    bgcolor: evalDemoMode ? '#fff8e1' : '#fcfcfc',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <FormControlLabel
                    control={
                      <Switch
                        checked={evalDemoMode}
                        onChange={(e) => setEvalDemoMode(e.target.checked)}
                        size="small"
                        color="warning"
                      />
                    }
                    label={
                      <Typography variant="body2" fontWeight={700} color={evalDemoMode ? "warning.dark" : "text.secondary"}>
                        🧪 Eval / Demo Mode
                      </Typography>
                    }
                    sx={{ m: 0 }}
                  />
                </Paper>
                <Link href="/preview" style={{ textDecoration: 'none' }}>
                  <Button
                    variant="outlined"
                    startIcon={<OpenInNewIcon />}
                    sx={{
                      borderRadius: '980px',
                      py: 1.2,
                      px: 3,
                      fontWeight: 600,
                      textTransform: 'none',
                    }}
                  >
                    View Public Site
                  </Button>
                </Link>
                <Button
                  variant="contained"
                  startIcon={<CloudUploadIcon />}
                  onClick={() => setUploadModalOpen(true)}
                  sx={{
                    borderRadius: '980px',
                    bgcolor: '#0071e3',
                    py: 1.2,
                    px: 4,
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: 'none',
                    '&:hover': { bgcolor: '#0077ed', boxShadow: 'none' }
                  }}
                >
                  Upload Newsletter
                </Button>
              </Stack>
            </Box>

            {/* Stats Overview */}
            <Grid container spacing={3} sx={{ mt: 3, mb: 2 }}>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Link href="/subscribers" style={{ textDecoration: 'none' }}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0', cursor: 'pointer', '&:hover': { borderColor: 'primary.light' } }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                      <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#e8f2ff', color: '#0071e3', display: 'flex' }}>
                        <PeopleIcon />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary" fontWeight={500}>Active Subscribers</Typography>
                        <Typography variant="h6" fontWeight={700}>{subscribersCount}</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Link>
              </Grid>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Link href="#newsletters-feed" style={{ textDecoration: 'none' }}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0', cursor: 'pointer', '&:hover': { borderColor: 'primary.light' } }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                      <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#e6f4ea', color: '#137333', display: 'flex' }}>
                        <ArticleIcon />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary" fontWeight={500}>Total Publications</Typography>
                        <Typography variant="h6" fontWeight={700}>{publicNewsletters.length}</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Link>
              </Grid>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Link href="/errors" style={{ textDecoration: 'none' }}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0', cursor: 'pointer', '&:hover': { borderColor: 'error.light' } }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                      <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#fff0e6', color: '#d93025', display: 'flex' }}>
                        <WarningIcon />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary" fontWeight={500}>Validation Failures</Typography>
                        <Typography variant="h6" fontWeight={700} sx={{ color: '#d93025' }}>{errorLogs.length}</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Link>
              </Grid>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0' }}>
                  <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                    <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#fbf0ff', color: '#a142f4', display: 'flex' }}>
                      <ScheduleIcon />
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" fontWeight={500}>Pending Approvals</Typography>
                      <Typography variant="h6" fontWeight={700} sx={{ color: '#a142f4' }}>{pendingApprovals.length}</Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

          </Container>
        </Box>
      )}

      {/* 3. MAIN DASHBOARD CONTENT */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        
        {/* If Logged In: Show Admin Approval Table & Error logs */}
        {user && (
          <Box>
            
            {/* Row 1: Human-in-the-Middle Approvals */}
            {pendingApprovals.length > 0 && (
              <Paper sx={{ p: 3, mb: 4, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 2, color: '#1d1d1f' }}>
                  🔔 Human-in-the-Middle Approvals ({pendingApprovals.length})
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#fafafa' }}>
                        <TableCell sx={{ fontWeight: 600 }}>File Name</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Target Sunday</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Upload Date</TableCell>
                        <TableCell sx={{ fontWeight: 600 }} align="right">Quick Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {pendingApprovals.map((item) => (
                        <TableRow key={item.id} hover>
                          <TableCell sx={{ fontWeight: 500 }}>{item.filename}</TableCell>
                          <TableCell>{item.target_sunday ? new Date(item.target_sunday).toLocaleDateString() : 'N/A'}</TableCell>
                          <TableCell color="text.secondary">
                            {item.uploaded_at ? new Date(item.uploaded_at).toLocaleDateString() : 'Recent'}
                          </TableCell>
                          <TableCell align="right">
                            <Stack direction="row" spacing={1} justifyContent="flex-end">
                              <Button 
                                variant="contained" 
                                color="success" 
                                size="small" 
                                startIcon={<CheckCircleIcon />} 
                                onClick={() => handleApprove(item.id)}
                                sx={{ textTransform: 'none', borderRadius: 2 }}
                              >
                                Approve
                              </Button>
                              <Button 
                                variant="outlined" 
                                color="primary" 
                                size="small" 
                                startIcon={<RefreshIcon />} 
                                onClick={() => handleRegenerate(item.id)}
                                sx={{ textTransform: 'none', borderRadius: 2 }}
                              >
                                Regenerate
                              </Button>
                              <Button 
                                variant="text" 
                                color="error" 
                                size="small" 
                                startIcon={<CancelIcon />} 
                                onClick={() => handleReject(item.id)}
                                sx={{ textTransform: 'none' }}
                              >
                                Reject
                              </Button>
                            </Stack>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            )}



            {/* Row 3: Latest Scheduled Newsletter */}
            {latestScheduled && (
              <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 3, color: '#1d1d1f' }}>
                  📅 Upcoming Scheduled Newsletter {latestScheduled.scheduled_at ? '(Custom Schedule)' : '(Sunday Morning Delivery)'}
                </Typography>
                
                <Grid container spacing={4} alignItems="center">
                  {latestScheduled.thumbnail_id && (
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 3, overflow: 'hidden', boxShadow: '0 6px 20px rgba(0,0,0,0.06)' }}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img 
                          src={`${backendUrl}/newsletters/${latestScheduled.id}/thumbnail`} 
                          alt="Thumbnail preview"
                          style={{ width: '100%', display: 'block' }}
                        />
                      </Box>
                    </Grid>
                  )}
                  <Grid size={{ xs: 12, md: latestScheduled.thumbnail_id ? 8 : 12 }}>
                    <Typography variant="caption" sx={{ color: '#0071e3', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
                      {latestScheduled.scheduled_at ? (
                        <>
                          ⏱️ Scheduled For: {new Date(latestScheduled.scheduled_at).toLocaleString(undefined, {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </>
                      ) : (
                        <>
                          📅 Scheduled Sunday: {latestScheduled.target_sunday ? new Date(latestScheduled.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { 
                            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
                          }) : ''} (Sunday morning)
                        </>
                      )}
                    </Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ my: 1 }}>
                      {latestScheduled.title}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#515154', mb: 3, whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                      {latestScheduled.summary}
                    </Typography>
                    
                    <Stack direction="row" spacing={2} useFlexGap flexWrap="wrap">
                      <Button
                        variant="contained"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenEditScheduled(latestScheduled)}
                        sx={{ textTransform: 'none', borderRadius: 2, bgcolor: '#0071e3', px: 3 }}
                      >
                        Edit Schedule & Content
                      </Button>
                      <Button 
                        variant="outlined" 
                        startIcon={<DownloadIcon />} 
                        href={`${backendUrl}/newsletters/${latestScheduled.id}/download`}
                        target="_blank"
                        sx={{ textTransform: 'none', borderRadius: 2, px: 3 }}
                      >
                        Download original
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        onClick={() => handleCancelSchedule(latestScheduled.id)}
                        sx={{ textTransform: 'none', borderRadius: 2, px: 3 }}
                      >
                        Cancel Scheduled Delivery
                      </Button>
                    </Stack>

                  </Grid>
                </Grid>
              </Paper>
            )}

          </Box>
        )}

        {/* Public Feed (For non-authenticated users, or lower section list of published issues) */}
        <Box sx={{ mt: user ? 6 : 0 }} id="newsletters-feed">
          <Typography variant="h4" sx={{ mb: 4, letterSpacing: '-0.02em', fontWeight: 700 }}>
            {user ? 'All Published Newsletters' : 'Latest Newsletters'}
          </Typography>

          {/* Tag Filter Chips Row */}
          {!fetchingNewsletters && publicNewsletters.length > 0 && (() => {
            const allTags = Array.from(
              new Set(
                publicNewsletters
                  .filter(n => !user || n.status === 'delivered')
                  .flatMap(n => n.tags ? n.tags.split(',').map((t: string) => t.trim().toLowerCase()) : [])
              )
            ).filter(Boolean);

            if (allTags.length === 0) return null;

            return (
              <Stack 
                direction="row" 
                spacing={1} 
                sx={{ 
                  mb: 4, 
                  overflowX: 'auto', 
                  pb: 1.5,
                  scrollbarWidth: 'none',
                  '&::-webkit-scrollbar': { display: 'none' } 
                }}
              >
                <Chip
                  label="All Issues"
                  onClick={() => setSelectedTag(null)}
                  color={selectedTag === null ? "primary" : "default"}
                  variant={selectedTag === null ? "filled" : "outlined"}
                  sx={{ fontWeight: 600, borderRadius: '980px', px: 1.5 }}
                />
                {allTags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag.replace(/-/g, ' ')}
                    onClick={() => setSelectedTag(tag)}
                    color={selectedTag === tag ? "primary" : "default"}
                    variant={selectedTag === tag ? "filled" : "outlined"}
                    sx={{ fontWeight: 600, textTransform: 'capitalize', borderRadius: '980px', px: 1.5 }}
                  />
                ))}
              </Stack>
            );
          })()}

          {fetchingNewsletters ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
              <CircularProgress />
            </Box>
          ) : publicNewsletters.length > 0 ? (() => {
            const filteredNewsletters = publicNewsletters
              .filter(n => !user || n.status === 'delivered')
              .filter(n => {
                if (!selectedTag) return true;
                if (!n.tags) return false;
                const tagList = n.tags.split(',').map((t: string) => t.trim().toLowerCase());
                return tagList.includes(selectedTag);
              });

            if (filteredNewsletters.length === 0) {
              return (
                <Box sx={{ textAlign: 'center', py: 8, opacity: 0.6 }}>
                  <Typography variant="body1">No newsletters match the filter category &quot;{selectedTag}&quot;.</Typography>
                  <Button variant="text" onClick={() => setSelectedTag(null)} sx={{ mt: 1, textTransform: 'none' }}>
                    Clear Filter
                  </Button>
                </Box>
              );
            }

            return (
              <Grid container spacing={3}>
                {filteredNewsletters.map((item) => (
                  <Grid size={{ xs: 12, sm: 6, md: 4 }} key={item.id}>
                    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
                      <Typography variant="overline" color="primary" sx={{ fontWeight: 700 }}>
                        {item.target_sunday ? new Date(item.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric',
                          timeZone: 'UTC'
                        }) : item.uploaded_at ? new Date(item.uploaded_at).toLocaleDateString(undefined, {
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric'
                        }) : 'Recent'}
                      </Typography>
                      <Typography variant="h6" sx={{ mb: 0.5, fontWeight: 700, lineHeight: 1.3 }}>
                        {item.title || "Weekly Bulletin"}
                      </Typography>

                      {/* Display Tag Pills Inline inside Cards */}
                      {item.tags && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1, mb: 2 }}>
                          {item.tags.split(',').map((t: string) => {
                            const trimmed = t.trim().toLowerCase();
                            return (
                              <Chip
                                key={trimmed}
                                label={trimmed.replace(/-/g, ' ')}
                                size="small"
                                variant="outlined"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedTag(trimmed === selectedTag ? null : trimmed);
                                }}
                                sx={{ 
                                  fontSize: '0.7rem', 
                                  height: '20px', 
                                  textTransform: 'capitalize',
                                  borderRadius: '4px',
                                  borderColor: selectedTag === trimmed ? '#0071e3' : '#e5e5ea',
                                  color: selectedTag === trimmed ? '#0071e3' : '#8e8e93',
                                  bgcolor: selectedTag === trimmed ? '#e1f0ff' : 'transparent',
                                  '&:hover': { bgcolor: '#f2f8fc' }
                                }}
                              />
                            );
                          })}
                        </Box>
                      )}

                      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, flexGrow: 1, whiteSpace: 'pre-line', lineHeight: 1.6 }}>
                        {item.summary ? item.summary.substring(0, 200) + "..." : "Read the latest news from our parish community."}
                      </Typography>
                      
                      <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center">
                        <Button 
                          variant="text" 
                          color="primary" 
                          sx={{ p: 0, fontWeight: 600, textTransform: 'none' }}
                          onClick={() => {
                            setSelectedNewsletter(item);
                            setModalOpen(true);
                          }}
                        >
                          Read Summary →
                        </Button>
                        {item.drive_link && (
                          <IconButton 
                            size="small" 
                            color="default" 
                            href={item.drive_link} 
                            target="_blank"
                            title="Download original file"
                          >
                            <DownloadIcon fontSize="small" color="action" />
                          </IconButton>
                        )}
                      </Stack>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            );
          })() : (
            <Box sx={{ textAlign: 'center', py: 5, opacity: 0.6 }}>
              <ArticleIcon sx={{ fontSize: 48, mb: 1 }} color="disabled" />
              <Typography variant="body1">No newsletters have been published yet.</Typography>
            </Box>
          )}
        </Box>

      </Container>

      {/* 4. MOBILE FRIENDLY UPLOAD DIALOG MODAL */}
      <Dialog open={uploadModalOpen} onClose={() => setUploadModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          Upload Newsletter File
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload parish bulletin PDF or DOCX. The system will compress the document, extract contents, and generate summary details automatically.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ textAlign: 'center', py: 4, border: '2px dashed #d0d0d0', borderRadius: 3, bgcolor: '#fafafa' }}>
            <input
              type="file"
              id="modal-file-upload"
              hidden
              onChange={handleFileChange}
              accept=".pdf,.docx"
            />
            <label htmlFor="modal-file-upload">
              <IconButton color="primary" component="span" sx={{ p: 3, bgcolor: '#e8f2ff', mb: 2 }}>
                <CloudUploadIcon fontSize="large" />
              </IconButton>
            </label>
            <Typography variant="subtitle1" fontWeight={600}>
              {file ? file.name : "Select bulletin document"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              PDF or DOCX files up to 20MB
            </Typography>
          </Box>

          <Paper
            variant="outlined"
            sx={{
              mt: 3,
              p: 2,
              borderRadius: 2,
              borderColor: evalDemoMode ? '#ffa726' : '#e0e0e0',
              bgcolor: evalDemoMode ? '#fff8e1' : '#fafafa',
              transition: 'all 0.2s ease',
            }}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={evalDemoMode}
                  onChange={(e) => setEvalDemoMode(e.target.checked)}
                  color="warning"
                />
              }
              label={
                <Box>
                  <Typography variant="body2" fontWeight={700} color={evalDemoMode ? "warning.dark" : "text.primary"}>
                    🧪 Eval / Demo Mode (Immediate Submission Preview)
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Simulates scheduled process in one fell swoop. Sends sample preview email to <strong>{userEmail}</strong> with subject prefixed by <code>[DEMO/PREVIEW]</code>.
                  </Typography>
                </Box>
              }
              sx={{ width: '100%', m: 0 }}
            />
          </Paper>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setUploadModalOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={loading || !file}
            onClick={handleUpload}
            sx={{ bgcolor: '#0071e3', textTransform: 'none', px: 4, borderRadius: '980px' }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Summarize & Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 5. PUBLIC SUMMARY MODAL */}
      <Dialog 
        open={modalOpen} 
        onClose={() => setModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ pr: 6, fontWeight: 700 }}>
          {selectedNewsletter?.title || "Newsletter Summary"}
          <IconButton
            onClick={() => setModalOpen(false)}
            sx={{ position: 'absolute', right: 16, top: 16 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="overline" color="primary" sx={{ fontWeight: 700, mb: 2, display: 'block' }}>
            {selectedNewsletter?.target_sunday ? new Date(selectedNewsletter.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { 
              year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
            }) : selectedNewsletter?.uploaded_at ? new Date(selectedNewsletter.uploaded_at).toLocaleDateString(undefined, { 
              year: 'numeric', month: 'long', day: 'numeric' 
            }) : ''}
          </Typography>
          
          <Grid container spacing={3}>
            {selectedNewsletter?.thumbnail_id && (
              <Grid size={{ xs: 12, md: 4 }}>
                <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 2, overflow: 'hidden' }}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src={`${backendUrl}/newsletters/${selectedNewsletter.id}/thumbnail`} 
                    alt="Newsletter Thumbnail"
                    style={{ width: '100%', display: 'block' }}
                  />
                </Box>
              </Grid>
            )}
            <Grid size={{ xs: 12, md: selectedNewsletter?.thumbnail_id ? 8 : 12 }}>
              <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8, whiteSpace: 'pre-line' }}>
                {selectedNewsletter?.summary}
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setModalOpen(false)} variant="outlined" sx={{ borderRadius: '100px', px: 4 }}>
            Close
          </Button>
          {selectedNewsletter && (
            <Button 
              variant="outlined" 
              startIcon={<DownloadIcon />} 
              href={`${backendUrl}/newsletters/${selectedNewsletter.id}/download`} 
              target="_blank"
              sx={{ borderRadius: '100px', px: 4 }}
            >
              Download original
            </Button>
          )}
          {!user && (
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <Button variant="contained" sx={{ borderRadius: '100px', px: 4 }}>
                Join Mailing List
              </Button>
            </Link>
          )}
        </DialogActions>
      </Dialog>

      {/* 6. EDIT SCHEDULE & CONTENT DIALOG */}
      <Dialog 
        open={editScheduledOpen} 
        onClose={() => setEditScheduledOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ pr: 6, fontWeight: 700 }}>
          📅 Edit Schedule & Email Content
          <IconButton
            onClick={() => setEditScheduledOpen(false)}
            sx={{ position: 'absolute', right: 16, top: 16 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={3}>
            {/* Left Column: Form Inputs */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#1d1d1f' }}>
                ✏️ Edit Details
              </Typography>
              <Stack spacing={3}>
                <TextField
                  label="Email Subject"
                  fullWidth
                  value={editScheduledTitle}
                  onChange={(e) => setEditScheduledTitle(e.target.value)}
                  variant="outlined"
                  required
                />
                <TextField
                  label="Email Body / Summary"
                  fullWidth
                  multiline
                  rows={8}
                  value={editScheduledSummary}
                  onChange={(e) => setEditScheduledSummary(e.target.value)}
                  variant="outlined"
                  required
                  helperText="Use newlines to separate paragraphs."
                />
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
                    📅 Schedule Delivery Date
                  </Typography>
                  <TextField
                    type="date"
                    fullWidth
                    value={editScheduledDate}
                    onChange={(e) => setEditScheduledDate(e.target.value)}
                    variant="outlined"
                    required
                  />
                </Box>

                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
                    ⏱️ Schedule Delivery Time
                  </Typography>
                  <TextField
                    type="time"
                    fullWidth
                    value={editScheduledTime}
                    onChange={(e) => setEditScheduledTime(e.target.value)}
                    variant="outlined"
                    required
                  />
                </Box>
              </Stack>
            </Grid>

            {/* Right Column: Live Email Preview */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#1d1d1f' }}>
                📧 Live Email Preview
              </Typography>
              <Box sx={{ 
                border: '1px solid #e0e0e0', 
                borderRadius: 2, 
                p: 2, 
                bgcolor: '#f5f5f7',
                height: '100%',
                maxHeight: 520,
                overflowY: 'auto'
              }}>
                <Box sx={{ 
                  bgcolor: 'white', 
                  p: 3, 
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                  lineHeight: 1.6,
                  color: '#333'
                }}>
                  <Typography variant="h6" sx={{ color: '#0071e3', fontWeight: 700, mb: 2, borderBottom: '1px solid #eee', pb: 1, fontSize: '1.1rem' }}>
                    {editScheduledTitle || '(No Subject)'}
                  </Typography>
                  <Box sx={{ fontSize: '14px', whiteSpace: 'pre-line', mb: 3 }}>
                    {editScheduledSummary || '(No Content)'}
                  </Box>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="caption" sx={{ color: '#86868b', display: 'block', fontSize: '11px' }}>
                    Sent by Newsletter Herald. To unsubscribe, please visit the parish website.
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setEditScheduledOpen(false)} variant="outlined" sx={{ borderRadius: '100px', px: 4 }}>
            Cancel
          </Button>
          <Button 
            onClick={() => latestScheduled && handleSaveScheduledChanges(latestScheduled.id)} 
            variant="contained" 
            disabled={editScheduledSaving || !editScheduledTitle || !editScheduledSummary || !editScheduledDate || !editScheduledTime}
            sx={{ borderRadius: '100px', px: 4, bgcolor: '#0071e3' }}
          >
            {editScheduledSaving ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
