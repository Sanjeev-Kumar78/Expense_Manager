# Expense Manager Frontend

A modern, responsive React frontend for the Expense Manager application built with TypeScript, shadcn/ui components, and a beautiful green/black theme.

## Features

### ✨ UI/UX
- **Modern Design**: Clean, professional interface with green/black theme
- **Responsive Layout**: Mobile-first design that works on all devices
- **shadcn/ui Components**: Beautiful, accessible UI components
- **Dark Theme**: Eye-friendly dark theme with green accents

### 🔐 Authentication & Security
- **JWT-based Authentication**: Secure token-based authentication
- **Protected Routes**: Route guards to prevent unauthorized access
- **Persistent Sessions**: Automatic session restoration
- **Form Validation**: Client-side validation with error handling

### 📊 Dashboard & Analytics
- **Interactive Charts**: Beautiful charts using Recharts library
- **Real-time Metrics**: Key financial metrics at a glance
- **Category Breakdown**: Pie chart showing spending by category
- **Monthly Trends**: Bar chart showing spending patterns over time
- **Recent Transactions**: Quick view of latest expenses

### 🛡️ Route Safety
- **Protected Routes**: Automatic redirection for unauthenticated users
- **Route Guards**: Middleware to check authentication status
- **404 Handling**: Proper error pages for invalid routes
- **Navigation Guards**: Prevent access to restricted areas

## Technology Stack

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **React Router** - Client-side routing with protection
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality component library
- **Recharts** - Responsive chart library
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

4. **Start development server**
   ```bash
   npm start
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## Available Scripts

- `npm start` - Start development server
- `npm test` - Run test suite  
- `npm run build` - Build for production
- `npm run eject` - Eject from Create React App

## License

This project is licensed under the MIT License.