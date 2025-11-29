# MyTraderPal Frontend (React + Vite)

Simple React application built with Vite, TypeScript, and Tailwind CSS.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:9000
VITE_USER_POOL_ID=your-user-pool-id
VITE_USER_POOL_CLIENT_ID=your-client-id
VITE_AWS_REGION=us-east-1
```

## Project Structure

```
src/
├── components/     # Reusable UI components
│   └── ui/        # shadcn/ui components
├── lib/           # Utilities and API client
├── pages/         # Page components
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── NotesPage.tsx
│   └── StrategiesPage.tsx
├── App.tsx        # Main app with routing
└── main.tsx       # Entry point
```

## Features

- React Router for navigation
- AWS Amplify for authentication
- Tailwind CSS for styling
- TypeScript for type safety
- Vite for fast development

