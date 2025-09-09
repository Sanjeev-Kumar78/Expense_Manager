export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  budget?: number;
  created_at: string;
}

export interface Expense {
  id: string;
  amount: number;
  description: string;
  category: string;
  date: string;
  user_id: string;
  receipt_url?: string;
  merchant?: string;
  created_at: string;
}

export interface Transaction {
  id: string;
  amount: number;
  description: string;
  category: string;
  date: string;
  type: 'income' | 'expense';
  user_id: string;
  created_at: string;
}

export interface SpendingSummary {
  total_spent: number;
  total_transactions: number;
  categories: { [key: string]: number };
  monthly_summary: { [key: string]: number };
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  budget?: number;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}