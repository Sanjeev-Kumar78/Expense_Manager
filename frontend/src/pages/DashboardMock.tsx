import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContextMock';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';
import { 
  DollarSign, 
  CreditCard, 
  Target, 
  Calendar,
  Plus,
  Upload
} from 'lucide-react';

// Mock data for demo purposes
const mockSummary = {
  total_spent: 1256.78,
  total_transactions: 23,
  categories: {
    'Food & Dining': 450.23,
    'Transportation': 234.56,
    'Shopping': 178.90,
    'Entertainment': 156.45,
    'Bills & Utilities': 236.64
  },
  monthly_summary: {
    'Jan': 980.45,
    'Feb': 1120.30,
    'Mar': 1256.78
  }
};

const mockExpenses = [
  {
    id: '1',
    amount: 45.67,
    description: 'Lunch at Italian Restaurant',
    category: 'Food & Dining',
    date: '2024-03-15',
    merchant: 'Luigi\'s Bistro',
    user_id: '1',
    created_at: '2024-03-15'
  },
  {
    id: '2',
    amount: 23.50,
    description: 'Coffee and pastry',
    category: 'Food & Dining',
    date: '2024-03-14',
    merchant: 'Starbucks',
    user_id: '1',
    created_at: '2024-03-14'
  },
  {
    id: '3',
    amount: 89.99,
    description: 'New running shoes',
    category: 'Shopping',
    date: '2024-03-13',
    merchant: 'Nike Store',
    user_id: '1',
    created_at: '2024-03-13'
  },
  {
    id: '4',
    amount: 156.78,
    description: 'Electric bill',
    category: 'Bills & Utilities',
    date: '2024-03-12',
    merchant: 'PowerCorp',
    user_id: '1',
    created_at: '2024-03-12'
  },
  {
    id: '5',
    amount: 67.45,
    description: 'Gas station fill-up',
    category: 'Transportation',
    date: '2024-03-11',
    merchant: 'Shell',
    user_id: '1',
    created_at: '2024-03-11'
  }
];

const DashboardMock: React.FC = () => {
  const { user } = useAuth();
  const [summary] = useState(mockSummary);
  const [recentExpenses] = useState(mockExpenses);
  const [loading] = useState(false);

  // Prepare chart data
  const categoryData = Object.entries(summary.categories).map(([name, value]) => ({
    name,
    value,
    percentage: ((value / summary.total_spent) * 100).toFixed(1)
  }));

  const monthlyData = Object.entries(summary.monthly_summary).map(([month, amount]) => ({
    month,
    amount
  }));

  const COLORS = ['#22c55e', '#16a34a', '#15803d', '#166534', '#14532d', '#052e16'];

  const budgetUsed = user?.budget ? (summary.total_spent / user.budget) * 100 : 0;
  const budgetRemaining = user?.budget ? user.budget - summary.total_spent : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name || user?.username}!
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Upload Receipt
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Expense
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              ${summary.total_spent.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transactions</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {summary.total_transactions}
            </div>
            <p className="text-xs text-muted-foreground">
              Total transactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Budget Status</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {budgetUsed.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {user?.budget ? `$${budgetRemaining.toFixed(2)} remaining` : 'No budget set'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg per Day</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              ${(summary.total_spent / 30).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              Daily average
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Spending by Category</CardTitle>
            <CardDescription>
              Your expenses broken down by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: any) => [`$${value.toFixed(2)}`, 'Amount']}
                    labelFormatter={(label) => `Category: ${label}`}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Monthly Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Spending Trend</CardTitle>
            <CardDescription>
              Your spending pattern over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                  <Tooltip 
                    formatter={(value: any) => [`$${value.toFixed(2)}`, 'Amount']}
                    labelFormatter={(label) => `Month: ${label}`}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))'
                    }}
                  />
                  <Bar dataKey="amount" fill="#22c55e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Expenses */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Expenses</CardTitle>
          <CardDescription>
            Your latest expense transactions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentExpenses.map((expense) => (
              <div key={expense.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <div>
                    <p className="font-medium text-foreground">{expense.description}</p>
                    <p className="text-sm text-muted-foreground">
                      {expense.category} • {new Date(expense.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-foreground">${expense.amount.toFixed(2)}</p>
                  {expense.merchant && (
                    <p className="text-xs text-muted-foreground">{expense.merchant}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardMock;