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
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col h-[calc(100vh-6.5rem)] animate-fade-in">
      {/* Page Header */}
      <div className="mb-4 flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
            <Sparkles size={28} />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
              FootballWise AI Analyst
            </h1>
            <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-0.5">
              LangGraph Multi-Agent Engine • XGBoost • SHAP • RAG
            </p>
          </div>
        </div>
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-2 mb-4">
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="text-xs bg-slate-900/90 border border-slate-700/80 hover:border-blue-500/60 text-slate-300 hover:text-white px-3.5 py-2 rounded-xl transition-all duration-150 flex items-center gap-2 disabled:opacity-50 shadow-md font-medium"
          >
            <Sparkles size={13} className="text-indigo-400" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-2xl p-4 sm:p-6 overflow-y-auto space-y-4 shadow-2xl shadow-slate-950/40">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white'
                  : 'bg-slate-800 border border-slate-700 text-blue-400'
              }`}
            >
              {msg.sender === 'user' ? <User size={20} /> : <Bot size={22} />}
            </div>

            <div className={`max-w-2xl flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
              {/* Tool calls execution badges */}
              {msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {msg.toolCalls.map((tool, tIdx) => (
                    <span
                      key={tIdx}
                      className="text-[11px] font-mono bg-slate-950 border border-slate-800 text-slate-300 px-2.5 py-1 rounded-lg flex items-center gap-1.5 shadow-sm"
                    >
                      <Wrench size={12} className="text-blue-400" />
                      {tool}
                    </span>
                  ))}
                </div>
              )}

              {/* Unconfigured Warning Alert */}
              {msg.unconfigured && (
                <div className="mb-2 p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs flex items-center gap-2">
                  <AlertCircle size={16} className="shrink-0" />
                  <span>GROQ_API_KEY is not configured on the server. Set GROQ_API_KEY in server/.env to enable live LLM reasoning.</span>
                </div>
              )}

              {/* Message Content Bubble */}
              <div
                className={`p-4 sm:p-5 rounded-2xl text-sm leading-relaxed shadow-lg ${
                  msg.sender === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-none whitespace-pre-wrap font-medium'
                    : 'bg-slate-950/90 border border-slate-800/90 text-slate-200 rounded-tl-none'
                }`}
              >
                {msg.sender === 'assistant' ? (
                  <div className="text-sm text-slate-200 leading-relaxed">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        table: ({ ...props }) => (
                          <div className="overflow-x-auto my-3 border border-slate-800 rounded-xl shadow-md bg-slate-950/80">
                            <table className="w-full text-left text-xs border-collapse" {...props} />
                          </div>
                        ),
                        thead: ({ ...props }) => (
                          <thead className="bg-slate-900 text-slate-200 font-bold uppercase tracking-wider border-b border-slate-800" {...props} />
                        ),
                        tbody: ({ ...props }) => (
                          <tbody className="divide-y divide-slate-800/60 text-slate-300" {...props} />
                        ),
                        tr: ({ ...props }) => (
                          <tr className="hover:bg-slate-900/60 transition-colors" {...props} />
                        ),
                        th: ({ ...props }) => (
                          <th className="px-4 py-3 font-bold text-slate-200 border-b border-slate-800" {...props} />
                        ),
                        td: ({ ...props }) => (
                          <td className="px-4 py-2.5 text-slate-300" {...props} />
                        ),
                        h2: ({ ...props }) => (
                          <h2 className="text-base font-bold text-white mt-4 mb-2 border-b border-slate-800 pb-1.5 flex items-center gap-1.5" {...props} />
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
                          <strong className="font-bold text-white" {...props} />
                        ),
                        code: ({ ...props }) => (
                          <code className="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-md text-xs font-mono text-blue-400" {...props} />
                        ),
                        blockquote: ({ ...props }) => (
                          <blockquote className="border-l-2 border-blue-500/60 pl-3.5 my-2 text-slate-400 italic text-xs" {...props} />
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
            <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 text-blue-400 flex items-center justify-center shadow-md">
              <Bot size={22} />
            </div>
            <div className="bg-slate-950/90 border border-slate-800 px-4 py-3 rounded-2xl text-xs text-slate-400 flex items-center gap-2.5 shadow-md">
              <RefreshCw size={15} className="animate-spin text-blue-400" />
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
        className="mt-4 flex gap-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask AI Analyst (e.g., Predict Barcelona vs Real Madrid)..."
          disabled={loading}
          className="flex-1 bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-3.5 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all disabled:opacity-50 font-medium shadow-inner"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-6 py-3.5 rounded-xl font-bold text-sm flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20 border border-blue-400/20 active:scale-95"
        >
          <Send size={18} />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>
    </div>
  );
};

export default AIAssistantPage;

