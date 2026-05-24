'use client';

import React, { useState } from 'react';
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
  IconButton
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import SearchIcon from '@mui/icons-material/Search';
import FilePresentIcon from '@mui/icons-material/FilePresent';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CloseIcon from '@mui/icons-material/Close';
import { useUser } from "@stackframe/stack";
import Link from "next/link";

export default function Home() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <HomeContent />
    </React.Suspense>
  );
}

function HomeContent() {
  const user = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [publicNewsletters, setPublicNewsletters] = useState<any[]>([]);
  const [fetchingNewsletters, setFetchingNewsletters] = useState(false);
  
  // New state for confirmation and editing
  const [editMode, setEditMode] = useState(false);
  const [scheduleDate, setScheduleDate] = useState("");
  const [tags, setTags] = useState("");
  const [updating, setUpdating] = useState(false);
  
  // Modal state for viewing summaries
  const [selectedNewsletter, setSelectedNewsletter] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);

  React.useEffect(() => {
    fetchNewsletters();
  }, []);

  const fetchNewsletters = async () => {
    setFetchingNewsletters(true);
    try {
      const response = await fetch('http://localhost:8000/newsletters');
      if (response.ok) {
        const data = await response.json();
        setPublicNewsletters(data.newsletters);
      }
    } catch (err) {
      console.error("Failed to fetch newsletters:", err);
    } finally {
      setFetchingNewsletters(false);
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
      const response = await fetch('http://localhost:8000/upload-document', {
        method: 'POST',
        body: formData,
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '', 
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
      const response = await fetch(`http://localhost:8000/newsletters/${summary.newsletter_id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
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

  return (
    <Box>
      {/* Hero Section */}
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
                  letterSpacing: '-0.04em'
                }}
              >
                Stay Connected with <br /> 
                <Box component="span" sx={{ color: 'text.secondary' }}>Your Parish.</Box>
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
            {!user ? (
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
                <Link href="/handler/sign-up" style={{ textDecoration: 'none' }}>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    size="large"
                    sx={{ borderRadius: '100px', px: 6, py: 2, fontSize: '1.1rem', width: { xs: '100%', sm: 'auto' } }}
                  >
                    Sign up for the newsletter
                  </Button>
                </Link>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  size="large"
                  sx={{ borderRadius: '100px', px: 6, py: 2, fontSize: '1.1rem', width: { xs: '100%', sm: 'auto' } }}
                  onClick={() => document.getElementById('newsletters-feed')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  Browse Newsletters
                </Button>
              </Stack>
            ) : (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Welcome back! Ready to summarize a new newsletter?
                </Typography>
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 1, 
                    display: 'flex', 
                    alignItems: 'center', 
                    border: '1px solid #e0e0e0',
                    borderRadius: '100px',
                    pl: 3,
                    transition: 'border-color 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      borderColor: 'primary.main',
                      boxShadow: '0 0 0 4px rgba(0,0,0,0.05)'
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1, overflow: 'hidden' }}>
                    <SearchIcon color="action" sx={{ mr: 1, opacity: 0.5 }} />
                    <Typography 
                      variant="body1" 
                      color={file ? "text.primary" : "text.secondary"}
                      sx={{ 
                        whiteSpace: 'nowrap', 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        fontWeight: file ? 500 : 400
                      }}
                    >
                      {file ? file.name : "Select a newsletter file..."}
                    </Typography>
                  </Box>
                  <input
                    type="file"
                    id="file-upload"
                    hidden
                    onChange={handleFileChange}
                    accept=".pdf,.docx"
                  />
                  <label htmlFor="file-upload">
                    <Button 
                      component="span" 
                      variant="text" 
                      color="inherit" 
                      sx={{ borderRadius: '100px', px: 2, mr: 1 }}
                    >
                      Browse
                    </Button>
                  </label>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    disabled={loading || !file}
                    onClick={handleUpload}
                    sx={{ 
                      borderRadius: '100px', 
                      px: 4, 
                      py: 1.5,
                      minWidth: '120px'
                    }}
                  >
                    {loading ? <CircularProgress size={24} color="inherit" /> : "Summarize"}
                  </Button>
                </Paper>
              </Box>
            )}
            
            {error && (
              <Alert severity="error" sx={{ mt: 2, borderRadius: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </Container>
      </Box>

      {/* Results Section */}
      <Container maxWidth="lg" sx={{ py: 10 }} id="newsletters-feed">
        {!user && (
          <Box sx={{ mb: 8 }}>
            <Typography variant="h4" sx={{ mb: 4, letterSpacing: '-0.02em', fontWeight: 700 }}>
              Latest Newsletters
            </Typography>
            {fetchingNewsletters ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
                <CircularProgress />
              </Box>
            ) : publicNewsletters.length > 0 ? (
              <Grid container spacing={3}>
                {publicNewsletters.map((item) => (
                  <Grid item xs={12} sm={6} md={4} key={item.id}>
                    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', borderRadius: 2 }}>
                      <Typography variant="overline" color="primary" sx={{ fontWeight: 700 }}>
                        {item.uploaded_at ? new Date(item.uploaded_at).toLocaleDateString(undefined, { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        }) : 'Recent'}
                      </Typography>
                      <Typography variant="h6" sx={{ mb: 1, fontWeight: 700 }}>
                        {item.title || "Weekly Bulletin"}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, flexGrow: 1, whiteSpace: 'pre-line' }}>
                        {item.summary ? item.summary.substring(0, 200) + "..." : "Read the latest news from our parish community."}
                      </Typography>
                      <Button 
                        variant="text" 
                        color="primary" 
                        sx={{ alignSelf: 'flex-start', p: 0, fontWeight: 600 }}
                        onClick={() => {
                          setSelectedNewsletter(item);
                          setModalOpen(true);
                        }}
                      >
                        Read Summary →
                      </Button>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box sx={{ textAlign: 'center', py: 5, opacity: 0.6 }}>
                <ArticleIcon sx={{ fontSize: 48, mb: 1 }} color="disabled" />
                <Typography variant="body1">No newsletters have been published yet.</Typography>
              </Box>
            )}
          </Box>
        )}

        {user && !summary && !loading && (
          <Box sx={{ textAlign: 'center', opacity: 0.5, py: 8 }}>
            <ArticleIcon sx={{ fontSize: 80, mb: 2, color: 'divider' }} />
            <Typography variant="h6" color="text.secondary">
              Upload a newsletter to see the summary here
            </Typography>
          </Box>
        )}

        {user && loading && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <CircularProgress size={40} sx={{ mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Processing your newsletter...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              We're using AI to extract and summarize the content.
            </Typography>
          </Box>
        )}

        {user && summary && (
          <Grow in timeout={500}>
            <Box>
              <Typography variant="h4" sx={{ mb: 4, letterSpacing: '-0.02em' }}>
                Latest Summary
              </Typography>
              <Grid container spacing={4}>
                <Grid item xs={12} md={8}>
                  <Paper sx={{ p: { xs: 3, md: 5 }, bgcolor: 'white' }}>
                    <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
                      <Chip 
                        icon={<AutoAwesomeIcon sx={{ fontSize: '16px !important' }} />} 
                        label={`AI Generated by ${summary.model}`} 
                        size="small" 
                        variant="outlined" 
                        sx={{ fontWeight: 600 }}
                      />
                      <Chip 
                        icon={<AccessTimeIcon sx={{ fontSize: '16px !important' }} />} 
                        label="Just now" 
                        size="small" 
                        variant="outlined" 
                        sx={{ fontWeight: 600 }}
                      />
                    </Stack>

                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
                      {summary.thumbnail_drive_id && (
                        <Box 
                          sx={{ 
                            width: { xs: '100%', md: '250px' }, 
                            flexShrink: 0,
                            border: '1px solid #e0e0e0',
                            borderRadius: 2,
                            overflow: 'hidden',
                            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                          }}
                        >
                          <img 
                            src={`https://drive.google.com/thumbnail?id=${summary.thumbnail_drive_id}&sz=w1000`} 
                            alt="Newsletter Preview" 
                            style={{ width: '100%', display: 'block' }}
                          />
                        </Box>
                      )}
                      
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontSize: '1.25rem', 
                          lineHeight: 1.8, 
                          whiteSpace: 'pre-line',
                          color: 'text.primary',
                          flexGrow: 1
                        }}
                      >
                        {summary.summary}
                      </Typography>
                    </Box>

                    <Divider sx={{ my: 4 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        Token count: <strong>{summary.tokens}</strong>
                      </Typography>
                      <Stack direction="row" spacing={2}>
                        {summary.drive_file_id && (
                          <Button 
                            variant="outlined" 
                            color="primary" 
                            href={`https://drive.google.com/uc?id=${summary.drive_file_id}&export=download`}
                            target="_blank"
                          >
                            Download PDF
                          </Button>
                        )}
                        <Button variant="contained" color="primary" onClick={() => window.print()}>
                          Print Summary
                        </Button>
                      </Stack>
                    </Box>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  {editMode ? (
                    <Paper sx={{ p: 3, bgcolor: 'white', mb: 3, border: '2px solid', borderColor: 'primary.light' }}>
                      <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                        <AutoAwesomeIcon color="primary" sx={{ mr: 1, fontSize: 20 }} />
                        Confirm Schedule
                      </Typography>
                      
                      <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                        The AI extracted these details. Please verify before scheduling delivery.
                      </Typography>

                      <Stack spacing={2.5}>
                        <TextField
                          label="Schedule Delivery For"
                          type="date"
                          value={scheduleDate}
                          onChange={(e) => setScheduleDate(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                          fullWidth
                          size="small"
                        />
                        
                        <TextField
                          label="Categorization Tags"
                          placeholder="e.g. lent, year-c"
                          value={tags}
                          onChange={(e) => setTags(e.target.value)}
                          fullWidth
                          size="small"
                          helperText="Comma separated"
                        />

                        <Button 
                          variant="contained" 
                          fullWidth 
                          size="large"
                          onClick={handleConfirm}
                          disabled={updating}
                          sx={{ borderRadius: '8px', py: 1.5 }}
                        >
                          {updating ? <CircularProgress size={24} /> : "Schedule Delivery"}
                        </Button>
                        
                        <Button 
                          variant="text" 
                          fullWidth 
                          onClick={() => setEditMode(false)}
                          disabled={updating}
                        >
                          Keep as Draft
                        </Button>
                      </Stack>
                    </Paper>
                  ) : (
                    <Paper sx={{ p: 3, bgcolor: 'white', mb: 3 }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>Status</Typography>
                      <Alert severity="success" icon={<AutoAwesomeIcon />} sx={{ mb: 2 }}>
                        Summarized & Scheduled
                      </Alert>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Date:</strong> {scheduleDate || 'Not set'}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        <strong>Tags:</strong> {tags || 'None'}
                      </Typography>
                      <Button variant="outlined" fullWidth onClick={() => setEditMode(true)}>
                        Edit Schedule
                      </Button>
                    </Paper>
                  )}

                  <Paper sx={{ p: 3, bgcolor: 'white' }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>File Details</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <FilePresentIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="body2" sx={{ fontWeight: 500, wordBreak: 'break-all' }}>
                        {file?.name}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Size: {(file?.size ? file.size / 1024 : 0).toFixed(2)} KB
                    </Typography>
                    <Button variant="contained" fullWidth color="primary" sx={{ mb: 1 }}>
                      Download Original
                    </Button>
                    <Button variant="text" fullWidth color="inherit">
                      Archive Newsletter
                    </Button>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          </Grow>
        )}
      </Container>

      {/* Public Summary Modal */}
      <Dialog 
        open={modalOpen} 
        onClose={() => setModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ pr: 6 }}>
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
            {selectedNewsletter?.uploaded_at ? new Date(selectedNewsletter.uploaded_at).toLocaleDateString(undefined, { 
              year: 'numeric', month: 'long', day: 'numeric' 
            }) : ''}
          </Typography>
          <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8, whiteSpace: 'pre-line' }}>
            {selectedNewsletter?.summary}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setModalOpen(false)} variant="outlined" sx={{ borderRadius: '100px', px: 4 }}>
            Close
          </Button>
          {!user && (
            <Link href="/handler/sign-up" style={{ textDecoration: 'none' }}>
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
