'use client';

import MainLayout from '@/components/layout/MainLayout';
import AgentList from '@/components/agents/AgentList';

export default function AgentsPage() {
  return (
    <MainLayout>
      <AgentList />
    </MainLayout>
  );
}
