import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Wrench, AlertCircle, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { sendChatMessage } from '../api';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  toolCalls?: string[];
  timestamp: string;
  unconfigured?: boolean;
}

const AIAssistantPage: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am FootballWise AI Analyst, powered by LangGraph, XGBoost, and StatsBomb RAG event data. Ask me to predict match outcomes, explain model predictions using SHAP, compare player/team metrics, or retrieve historical match event timelines!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const quickPrompts = [
    'Predict Barcelona vs Real Madrid and explain why.',
    'Compare Lionel Messi and Sergio Busquets stats.',
    'What are Barcelona\'s xG and passing accuracy numbers?',
    'Search past matches between Barcelona and Real Madrid.',
  ];

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(textToSend);
      const data = res.data;

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: data.response || 'No response returned.',
        toolCalls: data.tool_calls || [],
        unconfigured: data.unconfigured || false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: `Error connecting to AI Analyst service: ${err?.response?.data?.detail || err.message || 'Server error'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 flex flex-col h-[calc(100vh-6rem)]">
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Sparkles className="text-primary" size={26} />
            FootballWise AI Analyst
          </h1>
          <p className="text-sm text-textSecondary mt-1">
            Multi-agent intelligence powered by LangGraph, XGBoost ML, SHAP explainability, and StatsBomb RAG.
          </p>
        </div>
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-2 mb-4">
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="text-xs bg-surface border border-slate-700 hover:border-primary/50 text-slate-300 hover:text-white px-3 py-1.5 rounded-full transition-all duration-150 flex items-center gap-1.5 disabled:opacity-50"
          >
            <Sparkles size={12} className="text-primary" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 bg-surface border border-slate-700/80 rounded-xl p-4 overflow-y-auto space-y-4 shadow-inner">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-primary text-white'
                  : 'bg-slate-800 border border-slate-700 text-primary'
              }`}
            >
              {msg.sender === 'user' ? <User size={18} /> : <Bot size={20} />}
            </div>

            <div className={`max-w-2xl flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
              {/* Tool calls execution badges */}
              {msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {msg.toolCalls.map((tool, tIdx) => (
                    <span
                      key={tIdx}
                      className="text-[11px] font-mono bg-slate-800 border border-slate-700 text-slate-300 px-2 py-0.5 rounded flex items-center gap-1"
                    >
                      <Wrench size={11} className="text-primary" />
                      {tool}
                    </span>
                  ))}
                </div>
              )}

              {/* Unconfigured Warning Alert */}
              {msg.unconfigured && (
                <div className="mb-2 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-300 text-xs flex items-center gap-2">
                  <AlertCircle size={16} className="shrink-0" />
                  <span>GROQ_API_KEY is not configured on the server. Set GROQ_API_KEY in server/.env to enable live LLM reasoning.</span>
                </div>
              )}

              {/* Message Content Bubble */}
              <div
                className={`p-4 rounded-xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-primary text-white rounded-tr-none whitespace-pre-wrap'
                    : 'bg-slate-800/90 border border-slate-700/60 text-slate-200 rounded-tl-none shadow-sm'
                }`}
              >
                {msg.sender === 'assistant' ? (
                  <div className="text-sm text-slate-200 leading-relaxed">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        table: ({ ...props }) => (
                          <div className="overflow-x-auto my-3 border border-slate-700/80 rounded-lg shadow-sm bg-slate-900/60">
                            <table className="w-full text-left text-xs border-collapse" {...props} />
                          </div>
                        ),
                        thead: ({ ...props }) => (
                          <thead className="bg-slate-800/90 text-slate-200 font-semibold border-b border-slate-700" {...props} />
                        ),
                        tbody: ({ ...props }) => (
                          <tbody className="divide-y divide-slate-800 text-slate-300" {...props} />
                        ),
                        tr: ({ ...props }) => (
                          <tr className="hover:bg-slate-800/40 transition-colors" {...props} />
                        ),
                        th: ({ ...props }) => (
                          <th className="px-3.5 py-2.5 font-semibold text-slate-200 border-b border-slate-700" {...props} />
                        ),
                        td: ({ ...props }) => (
                          <td className="px-3.5 py-2 text-slate-300" {...props} />
                        ),
                        h2: ({ ...props }) => (
                          <h2 className="text-base font-bold text-white mt-4 mb-2 border-b border-slate-700/60 pb-1 flex items-center gap-1.5" {...props} />
                        ),
                        h3: ({ ...props }) => (
                          <h3 className="text-sm font-semibold text-slate-200 mt-3 mb-1" {...props} />
                        ),
                        ul: ({ ...props }) => (
                          <ul className="list-disc list-inside space-y-1.5 my-2 text-slate-300 pl-1" {...props} />
                        ),
                        ol: ({ ...props }) => (
                          <ol className="list-decimal list-inside space-y-1.5 my-2 text-slate-300 pl-1" {...props} />
                        ),
                        li: ({ ...props }) => (
                          <li className="my-0.5 text-slate-300 leading-relaxed" {...props} />
                        ),
                        p: ({ ...props }) => (
                          <p className="my-2 text-slate-200 leading-relaxed" {...props} />
                        ),
                        strong: ({ ...props }) => (
                          <strong className="font-semibold text-white" {...props} />
                        ),
                        code: ({ ...props }) => (
                          <code className="bg-slate-900 border border-slate-700/80 px-1.5 py-0.5 rounded text-xs font-mono text-primary" {...props} />
                        ),
                        blockquote: ({ ...props }) => (
                          <blockquote className="border-l-2 border-primary/60 pl-3 my-2 text-slate-400 italic text-xs" {...props} />
                        ),
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </div>
                ) : (
                  msg.text
                )}
              </div>

              <span className="text-[10px] text-slate-500 mt-1 px-1">{msg.timestamp}</span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 text-primary flex items-center justify-center">
              <Bot size={20} />
            </div>
            <div className="bg-slate-800/90 border border-slate-700 px-4 py-3 rounded-xl text-xs text-slate-400 flex items-center gap-2">
              <RefreshCw size={14} className="animate-spin text-primary" />
              <span>Analyzing tools and executing LangGraph workflow...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="mt-4 flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask AI Analyst (e.g., Predict Barcelona vs Real Madrid)..."
          disabled={loading}
          className="flex-1 bg-surface border border-slate-700 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-primary transition-all duration-150 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-primary hover:bg-primary/90 text-white px-5 py-3 rounded-lg font-medium text-sm flex items-center gap-2 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
        >
          <Send size={16} />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>
    </div>
  );
};

export default AIAssistantPage;
