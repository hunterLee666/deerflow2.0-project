'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Bot,
  MessageSquare,
  ListTodo,
  Brain,
  Settings,
  Users,
} from 'lucide-react';

interface SidebarProps {
  isAdmin?: boolean;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Conversations', href: '/conversations', icon: MessageSquare },
  { name: 'Tasks', href: '/tasks', icon: ListTodo },
  { name: 'Memory', href: '/memory', icon: Brain },
];

const adminNavigation = [
  { name: 'Users', href: '/admin/users', icon: Users },
  { name: 'Settings', href: '/admin/settings', icon: Settings },
];

export default function Sidebar({ isAdmin }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col bg-zinc-900 text-white">
      {/* Logo */}
      <div className="flex h-16 items-center px-6 border-b border-zinc-800">
        <Link href="/" className="flex items-center gap-2">
          <Bot className="h-8 w-8 text-blue-500" />
          <span className="text-xl font-bold">DeerFlow</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}

        {isAdmin && (
          <>
            <div className="pt-4 mt-4 border-t border-zinc-800">
              <p className="px-3 text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                Admin
              </p>
              {adminNavigation.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
                    )}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800">
        <p className="text-xs text-zinc-500">
          DeerFlow Enterprise v2.0
        </p>
      </div>
    </div>
  );
}
