import { useState, useRef, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Loader2, Send, StopCircle } from 'lucide-react';
import { useApi } from '@/lib/api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatInterface({ agentId }: { agentId?: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { post } = useApi();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !agentId) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/agents/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          message: input,
          stream: true,
        }),
      });

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';
      let messageId = `assistant-${Date.now()}`;

      const processStream = async () => {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          assistantMessage += chunk;

          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage?.id === messageId) {
              return [
                ...prev.slice(0, -1),
                { ...lastMessage, content: assistantMessage }
              ];
            } else {
              return [
                ...prev,
                {
                  id: messageId,
                  role: 'assistant',
                  content: assistantMessage,
                  timestamp: new Date()
                }
              ];
            }
          });
        }

        setIsStreaming(false);
      };

      await processStream();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response');
      setIsStreaming(false);
    }
  };

  const handleStop = () => {
    // In a real implementation, this would send a signal to stop the stream
    setIsStreaming(false);
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle>Chat with Agent</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4">
          {messages.map(message => (
            <div
              key={message.id}
              className={`mb-4 flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p>{message.content}</p>
              </div>
            </div>
          ))}
          {isStreaming && (
            <div className="mb-4 flex justify-start">
              <div className="bg-muted rounded-lg p-3">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            </div>
          )}
          {error && (
            <div className="mb-4 flex justify-start">
              <div className="bg-destructive/10 text-destructive rounded-lg p-3">
                {error}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </ScrollArea>

        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isStreaming}
            />
            {isStreaming ? (
              <Button
                type="button"
                variant="secondary"
                onClick={handleStop}
                disabled={!isStreaming}
              >
                <StopCircle className="mr-2 h-4 w-4" />
                Stop
              </Button>
            ) : (
              <Button type="submit" disabled={!input.trim() || !agentId}>
                <Send className="mr-2 h-4 w-4" />
                Send
              </Button>
            )}
          </form>
        </div>
      </CardContent>
    </Card>
  );
}