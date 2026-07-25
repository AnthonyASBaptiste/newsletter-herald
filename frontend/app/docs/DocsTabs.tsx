"use client";

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ArticleIcon from '@mui/icons-material/Article';
import HistoryIcon from '@mui/icons-material/History';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Button from '@mui/material/Button';
import Link from 'next/link';

interface DocsTabsProps {
  adminGuide: string;
  changelog: string;
}

export default function DocsTabs({ adminGuide, changelog }: DocsTabsProps) {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f7', py: 6 }}>
      <Container maxWidth="md">
        
        {/* Back button and Title */}
        <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />}
                sx={{ borderRadius: '980px', textTransform: 'none', px: 2, borderColor: '#e0e0e0', color: '#1d1d1f', '&:hover': { borderColor: '#86868b', bgcolor: 'rgba(0,0,0,0.02)' } }}
              >
                Back
              </Button>
            </Link>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
              Documentation Center
            </Typography>
          </Box>
          
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            sx={{
              '& .MuiTabs-indicator': { bgcolor: '#0071e3' },
              '& .MuiTab-root': { textTransform: 'none', fontWeight: 600, fontSize: '0.95rem' },
              '& .Mui-selected': { color: '#0071e3 !important' }
            }}
          >
            <Tab icon={<ArticleIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Admin Manual" />
            <Tab icon={<HistoryIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Changelog" />
          </Tabs>
        </Box>

        {/* Document Render Paper */}
        <Paper sx={{ p: { xs: 3, md: 6 }, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.02)', border: '1px solid #e0e0e0', bgcolor: 'white' }}>
          {activeTab === 0 ? (
            <MarkdownRenderer content={adminGuide} />
          ) : (
            <MarkdownRenderer content={changelog} />
          )}
        </Paper>

      </Container>
    </Box>
  );
}

interface MarkdownRendererProps {
  content: string;
}

function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const lines = content.split('\n');
  const renderedElements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];
  let listType: 'ol' | 'ul' | null = null;
  let inCodeBlock = false;
  let codeLines: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Handle code blocks
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        renderedElements.push(
          <Box
            key={`code-${i}`}
            component="pre"
            sx={{
              p: 2.5,
              bgcolor: '#f5f5f7',
              borderRadius: 3,
              overflowX: 'auto',
              fontFamily: 'SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace',
              fontSize: '0.85rem',
              border: '1px solid #e3e3e8',
              my: 3.5,
              color: '#1d1d1f',
              lineHeight: 1.5
            }}
          >
            {codeLines.join('\n')}
          </Box>
        );
        codeLines = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    // Process lists (flushing them if the line is not a list item)
    const isUnordered = line.trim().startsWith('- ') || line.trim().startsWith('* ');
    const isOrdered = /^\d+\.\s/.test(line.trim());

    if (isUnordered || isOrdered) {
      const type = isUnordered ? 'ul' : 'ol';
      const cleanLine = isUnordered 
        ? line.trim().substring(2) 
        : line.trim().replace(/^\d+\.\s/, '');

      if (listType && listType !== type) {
        renderedElements.push(
          listType === 'ul' 
            ? <Box component="ul" key={`list-ul-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
            : <Box component="ol" key={`list-ol-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
        );
        currentList = [];
      }

      listType = type;
      currentList.push(
        <Box component="li" key={`item-${i}`} sx={{ mb: 1, lineHeight: 1.6, fontSize: '1.05rem' }}>
          {parseInlineMarkdown(cleanLine)}
        </Box>
      );
      continue;
    } else if (listType) {
      renderedElements.push(
        listType === 'ul' 
          ? <Box component="ul" key={`list-ul-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
          : <Box component="ol" key={`list-ol-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
      );
      currentList = [];
      listType = null;
    }

    // Handle horizontal rules
    if (line.trim() === '---') {
      renderedElements.push(<Divider key={`div-${i}`} sx={{ my: 4, borderColor: '#e0e0e0' }} />);
      continue;
    }

    // Handle headers
    if (line.startsWith('# ')) {
      renderedElements.push(
        <Typography variant="h4" key={`h1-${i}`} sx={{ fontWeight: 800, mt: 4, mb: 2.5, letterSpacing: '-0.03em', color: '#1d1d1f' }}>
          {parseInlineMarkdown(line.substring(2))}
        </Typography>
      );
    } else if (line.startsWith('## ')) {
      renderedElements.push(
        <Typography variant="h5" key={`h2-${i}`} sx={{ fontWeight: 700, mt: 4, mb: 2, letterSpacing: '-0.02em', color: '#1d1d1f' }}>
          {parseInlineMarkdown(line.substring(3))}
        </Typography>
      );
    } else if (line.startsWith('### ')) {
      renderedElements.push(
        <Typography variant="h6" key={`h3-${i}`} sx={{ fontWeight: 650, mt: 3, mb: 1.5, color: '#1d1d1f', letterSpacing: '-0.01em' }}>
          {parseInlineMarkdown(line.substring(4))}
        </Typography>
      );
    } else if (line.trim() === '') {
      renderedElements.push(<Box key={`space-${i}`} sx={{ height: 12 }} />);
    } else {
      renderedElements.push(
        <Typography variant="body1" key={`p-${i}`} sx={{ mb: 2, lineHeight: 1.65, fontSize: '1.05rem', color: '#333333' }}>
          {parseInlineMarkdown(line)}
        </Typography>
      );
    }
  }

  if (listType) {
    renderedElements.push(
      listType === 'ul' 
        ? <Box component="ul" key={`list-ul-final`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
        : <Box component="ol" key={`list-ol-final`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
    );
  }

  return <Box>{renderedElements}</Box>;
}

function parseInlineMarkdown(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let match;
  let lastIndex = 0;
  
  const linkMatches: { text: string; url: string; start: number; end: number }[] = [];
  while ((match = linkRegex.exec(text)) !== null) {
    linkMatches.push({
      text: match[1],
      url: match[2],
      start: match.index,
      end: linkRegex.lastIndex
    });
  }
  
  const parseBold = (str: string, keyPrefix: string): React.ReactNode[] => {
    const boldParts: React.ReactNode[] = [];
    const boldRegex = /\*\*([^*]+)\*\*/g;
    let boldMatch;
    let boldLastIndex = 0;
    let subIdx = 0;
    
    while ((boldMatch = boldRegex.exec(str)) !== null) {
      if (boldMatch.index > boldLastIndex) {
        boldParts.push(str.substring(boldLastIndex, boldMatch.index));
      }
      boldParts.push(<strong key={`${keyPrefix}-bold-${subIdx++}`} style={{ fontWeight: 700, color: '#1d1d1f' }}>{boldMatch[1]}</strong>);
      boldLastIndex = boldRegex.lastIndex;
    }
    if (boldLastIndex < str.length) {
      boldParts.push(str.substring(boldLastIndex));
    }
    return boldParts;
  };
  
  if (linkMatches.length === 0) {
    return parseBold(text, 'text');
  }
  
  linkMatches.forEach((link, idx) => {
    if (link.start > lastIndex) {
      parts.push(...parseBold(text.substring(lastIndex, link.start), `link-pre-${idx}`));
    }
    parts.push(
      <a href={link.url} key={`link-${idx}`} style={{ color: '#0071e3', textDecoration: 'none', fontWeight: 500 }} target={link.url.startsWith('http') ? '_blank' : undefined} rel={link.url.startsWith('http') ? 'noopener noreferrer' : undefined}>
        {link.text}
      </a>
    );
    lastIndex = link.end;
  });
  
  if (lastIndex < text.length) {
    parts.push(...parseBold(text.substring(lastIndex), 'link-post'));
  }
  
  return parts;
}
