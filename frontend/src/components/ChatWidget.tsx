'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { apiClient } from '@/lib/api-client';
import { handleChatError, getErrorMessage } from '@/lib/error-handler';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface Conversation {
  id: string;
  messages: Message[];
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sessionId] = useState(() => {
    // Get or create session ID
    if (typeof window !== 'undefined') {
      let sid = localStorage.getItem('chat_session_id');
      if (!sid) {
        sid = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('chat_session_id', sid);
      }
      return sid;
    }
    return `session_${Date.now()}`;
  });

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages]);

  // Focus input when widget opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Load conversation history on mount
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadConversations();
    }
  }, [isOpen]);

  const loadConversations = async () => {
    try {
      const response = await apiClient.get<{ conversations: Conversation[] }>(
        `/chat/conversations?session_id=${sessionId}&limit=1`
      );

      if (response.conversations && response.conversations.length > 0) {
        const latestConversation = response.conversations[0];
        setConversationId(latestConversation.id);

        // Load conversation messages
        const detailResponse = await apiClient.get<Conversation>(
          `/chat/conversations/${latestConversation.id}`
        );

        if (detailResponse.messages) {
          setMessages(detailResponse.messages);
        }
      }
    } catch (err) {
      console.error('Error loading conversations:', err);
      // Don't show error to user, just start fresh conversation
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);
    setIsLoading(true);

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: `temp_${Date.now()}`,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await apiClient.post<{
        conversation_id: string;
        message_id: string;
        role: string;
        content: string;
        created_at: string;
      }>('/chat/message', {
        conversation_id: conversationId,
        message: userMessage,
        session_id: sessionId,
        use_rag: true,
        topic_filter: null,
      });

      // Update conversation ID if new conversation
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.content,
        created_at: response.created_at,
      };

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMessage.id),
        { ...tempUserMessage, id: `user_${Date.now()}` },
        assistantMessage,
      ]);
    } catch (err: any) {
      console.error('Error sending message:', err);

      // Remove temp user message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));

      // Per errori gravi (500, network), redirect a pagina errore
      if (
        !err.response ||
        err.response?.status >= 500 ||
        err.code === 'ERR_NETWORK'
      ) {
        handleChatError(err);
        return;
      }

      // Per errori "minori" (validazione, rate limit), mostra inline
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const submitFeedback = async (feedback: 'thumbs_up' | 'thumbs_down') => {
    if (!conversationId) return;

    try {
      await apiClient.post('/chat/feedback', {
        conversation_id: conversationId,
        feedback,
      });
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        aria-label="Apri chat"
      >
        <MessageCircle className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex h-[600px] w-[400px] flex-col rounded-lg border bg-background shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b bg-primary p-4 text-primary-foreground rounded-t-lg">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          <div>
            <h3 className="font-semibold">AI Assistant</h3>
            <p className="text-xs opacity-90">AI Strategy Hub</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {conversationId && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearChat}
              className="h-8 text-primary-foreground hover:bg-primary-foreground/20"
            >
              Nuova chat
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(false)}
            className="h-8 w-8 text-primary-foreground hover:bg-primary-foreground/20"
            aria-label="Chiudi chat"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground">
            <MessageCircle className="mb-4 h-12 w-12 opacity-50" />
            <p className="text-sm px-4">
              Ciao! Sono il tuo assistente AI. Posso aiutarti a ricevere informazioni sui servizi erogati in ambito Cybersecurity, Compliance, AI e GDPR
            </p>
          </div>
        )}

        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  'max-w-[80%] rounded-lg px-4 py-2 text-sm',
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted',
                  message.role === 'assistant' && 'prose prose-sm max-w-none dark:prose-invert'
                )}
              >
                {message.role === 'assistant' ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      ul: ({ children }) => <ul className="mb-2 ml-4 list-disc space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      h1: ({ children }) => <h1 className="mb-2 text-lg font-bold">{children}</h1>,
                      h2: ({ children }) => <h2 className="mb-2 text-base font-bold">{children}</h2>,
                      h3: ({ children }) => <h3 className="mb-1 text-sm font-semibold">{children}</h3>,
                      code: ({ inline, children }) =>
                        inline ? (
                          <code className="rounded bg-muted-foreground/10 px-1 py-0.5 text-xs">{children}</code>
                        ) : (
                          <code className="block rounded bg-muted-foreground/10 p-2 text-xs">{children}</code>
                        ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                ) : (
                  message.content
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-lg bg-muted px-4 py-2 text-sm">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Sto pensando...</span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Error */}
      {error && (
        <div className="border-t px-4 py-2">
          <Alert variant="destructive">
            <AlertDescription className="text-xs">{error}</AlertDescription>
          </Alert>
        </div>
      )}

      {/* Feedback */}
      {conversationId && messages.length > 0 && !isLoading && (
        <div className="border-t px-4 py-2">
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <span>Questa risposta è stata utile?</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => submitFeedback('thumbs_up')}
              className="h-6 w-6 p-0"
            >
              <ThumbsUp className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => submitFeedback('thumbs_down')}
              className="h-6 w-6 p-0"
            >
              <ThumbsDown className="h-3 w-3" />
            </Button>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Scrivi un messaggio..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Questo chatbot è alimentato da AI e può commettere errori.
        </p>
      </div>
    </div>
  );
}
