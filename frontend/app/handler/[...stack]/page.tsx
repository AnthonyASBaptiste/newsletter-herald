import { StackHandler } from "@stackframe/stack";
import { stackServerApp } from "../../../stack/server";
import { Box } from "@mui/material";


export default function Handler(props: any) {
  return (
    <Box sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '80vh',
      py: 6,
      px: 2,
      bgcolor: '#f5f5f7'
    }}>
      <Box sx={{
        width: '100%',
        maxWidth: '440px',
        bgcolor: 'white',
        p: { xs: 3, sm: 4 },
        borderRadius: 4,
        boxShadow: '0 8px 32px rgba(0,0,0,0.04)',
        border: '1px solid #e0e0e0',
        '& > div': {
          width: '100% !important',
          margin: '0 !important',
          padding: '0 !important',
          boxShadow: 'none !important',
          border: 'none !important',
        }
      }}>
        <StackHandler app={stackServerApp} {...props} />
      </Box>
    </Box>
  );
}

