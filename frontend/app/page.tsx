'use client';

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Paper, 
  Grid, 
  CircularProgress,
  Fade,
  Grow,
  Alert,
  Divider,
  Stack,
  Chip,
  TextField,
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
  CardContent
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import SearchIcon from '@mui/icons-material/Search';
import FilePresentIcon from '@mui/icons-material/FilePresent';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
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
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useUser } from "@stackframe/stack";
import Link from "next/link";

export default function Home({ forcePublic = false }: { forcePublic?: boolean }) {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <HomeContent forcePublic={forcePublic} />
    </React.Suspense>
  );
}

function HomeContent({ forcePublic = false }: { forcePublic?: boolean }) {
  const stackUser = useUser();
  const user = forcePublic ? null : stackUser;
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [publicNewsletters, setPublicNewsletters] = useState<any[]>([]);
  const [fetchingNewsletters, setFetchingNewsletters] = useState(false);
  const [subscribersCount, setSubscribersCount] = useState(0);

  // New state for confirmation and editing
  const [editMode, setEditMode] = useState(false);
  const [scheduleDate, setScheduleDate] = useState("");
  const [tags, setTags] = useState("");
  const [updating, setUpdating] = useState(false);
  
  // Modal state for viewing summaries
  const [selectedNewsletter, setSelectedNewsletter] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Upload Modal State
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchNewsletters();
    if (user) {
      fetchSubscribersCount();
    }
  }, [user]);

  const fetchNewsletters = async () => {
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
  };

  const fetchSubscribersCount = async () => {
    try {
      const res = await fetch(`${backendUrl}/subscribers`);
      if (res.ok) {
        const data = await res.json();
        setSubscribersCount(data.stats?.active || 0);
      }
    } catch (err) {
      console.error("Failed to fetch subscribers stats:", err);
    }
  };

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
    setEditMode(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${backendUrl}/upload-document`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630', 
          'X-User-Email': user?.primaryEmail || 'anonymous',
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
      setEditMode(true);
      setUploadModalOpen(false); // Close modal on success
      setFile(null); // Clear selected file
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!summary || !summary.newsletter_id) return;

    setUpdating(true);
    try {
      const response = await fetch(`${backendUrl}/newsletters/${summary.newsletter_id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({
          schedule_date: scheduleDate || null,
          tags: tags || null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update newsletter schedule');
      }

      // Refresh public feed and exit edit mode
      fetchNewsletters();
      setEditMode(false);
      alert("Newsletter scheduled successfully!");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUpdating(false);
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
                  Welcome back, {user.primaryEmail}. Manage parish newsletters, approvals, and error states.
                </Typography>
              </Box>
              
              <Stack direction="row" spacing={2}>
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
                  📅 Upcoming Scheduled Newsletter (Next Sunday Delivery)
                </Typography>
                
                <Grid container spacing={4} alignItems="center">
                  {latestScheduled.thumbnail_id && (
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 3, overflow: 'hidden', boxShadow: '0 6px 20px rgba(0,0,0,0.06)' }}>
                        <img 
                          src={`${backendUrl}/newsletters/${latestScheduled.id}/thumbnail`} 
                          alt="Thumbnail preview"
                          style={{ width: '100%', display: 'block' }}
                        />
                      </Box>
                    </Grid>
                  )}
                  <Grid size={{ xs: 12, md: latestScheduled.thumbnail_id ? 8 : 12 }}>
                    <Typography variant="caption" sx={{ color: '#0071e3', fontWeight: 700, textTransform: 'uppercase' }}>
                      Scheduled Sunday: {latestScheduled.target_sunday ? new Date(latestScheduled.target_sunday).toLocaleDateString() : ''}
                    </Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ my: 1 }}>
                      {latestScheduled.title}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#515154', mb: 3, whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                      {latestScheduled.summary}
                    </Typography>
                    
                    <Stack direction="row" spacing={2}>
                      <Button 
                        variant="outlined" 
                        startIcon={<DownloadIcon />} 
                        href={`${backendUrl}/newsletters/${latestScheduled.id}/download`}
                        target="_blank"
                        sx={{ textTransform: 'none', borderRadius: 2 }}
                      >
                        Download original
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        onClick={() => handleCancelSchedule(latestScheduled.id)}
                        sx={{ textTransform: 'none', borderRadius: 2 }}
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
                  <Typography variant="body1">No newsletters match the filter category "{selectedTag}".</Typography>
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
                            color="action" 
                            href={item.drive_link} 
                            target="_blank"
                            title="Download original file"
                          >
                            <DownloadIcon fontSize="small" />
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
    </Box>
  );
}
