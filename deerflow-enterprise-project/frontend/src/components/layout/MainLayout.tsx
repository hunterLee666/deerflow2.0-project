'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '@/lib/hooks/useAuth';

interface MainLayoutProps {
  children: React.ReactNode;
}

const publicPaths = ['/login', '/register'];

export default function MainLayout({ children }: MainLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !publicPaths.includes(pathname)) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  // Don't apply layout to public pages
  if (publicPaths.includes(pathname)) {
    return <>{children}</>;
  }

  // Not authenticated, don't render
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0">
        <Sidebar isAdmin={false} />
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
