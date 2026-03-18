# Newsletter Herald Frontend

A modern dashboard for managing church newsletters and viewing AI-generated summaries.

## Tech Stack
- **Framework**: Next.js 15+ (App Router)
- **Styling**: Material UI (MUI) and Tailwind CSS
- **Authentication**: Stack Auth
- **State Management**: React Hooks and Context API

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` to view the application.

## Project Structure
- `app/`: Next.js 15 pages and layouts
- `app/components/`: Reusable MUI components
- `app/theme.ts`: Global MUI theme configuration
- `stack/`: Stack Auth client and server configuration

## Configuration
Ensure your `frontend/.env.local` contains the following Stack Auth credentials:
- `NEXT_PUBLIC_STACK_PROJECT_ID`
- `NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY`
- `STACK_SECRET_SERVER_KEY`

## Deployment
The frontend is designed to be deployed on Vercel or any other Next.js-compatible platform.

## Learn More
To learn more about Next.js, check out the [Next.js Documentation](https://nextjs.org/docs).
