// pages/ask-bis.tsx
import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { EmptyState } from '../components/EmptyState';
import { EvidenceRail } from '../components/EvidenceRail';

export default function AskBIS() {
  const [messages, setMessages] = useState<{role: string, text: string, citations?: any[]}[]>([]);
  const [input, setInput] = useState('');
  const [activeCitations, setActiveCitations] = useState<any[]>([]);

  const [isLoading, setIsLoading] = useState(false);
  const [conversationId] = useState(() => Math.random().toString(36).substring(7));

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId, message: userMessage, language: 'en' })
      });
      const data = await res.json();
      
      const botResponse = { 
        role: 'assistant', 
        text: data.answer,
        citations: data.citations?.map((c: any, idx: number) => ({
          id: idx,
          standard: c.document_title,
          clause: 'N/A', // Update with actual DB fields
          text: c.excerpt,
          confidence: 'Supported by source'
        })) || []
      };

      setMessages(prev => [...prev, botResponse]);
      setActiveCitations(botResponse.citations);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', text: 'System temporarily unavailable: Could not generate a verified answer.' }]);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <Layout>
      <div className="flex h-full border-t border-gray-200">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-gray-50 relative">
          <div className="flex-1 overflow-y-auto p-6">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <EmptyState 
                  title="Ask BIS Technical Assistant" 
                  description="Submit technical queries regarding Indian Standards, testing, and compliance." 
                />
              </div>
            ) : (
              <div className="max-w-3xl mx-auto space-y-6 pb-20">
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`p-4 text-sm max-w-[85%] border-l-4 ${m.role === 'user' ? 'bg-white border-blue-600 shadow-sm' : 'bg-gray-100 border-gray-800'}`}>
                      <span className="font-semibold block mb-1 text-xs text-gray-500 uppercase tracking-wide">
                        {m.role === 'user' ? 'User Query' : 'System Response'}
                      </span>
                      <p className="text-gray-900 leading-relaxed">{m.text}</p>
                      
                      {m.citations && (
                        <button 
                          onClick={() => setActiveCitations(m.citations || [])}
                          className="mt-3 text-blue-700 font-medium text-xs hover:underline flex items-center"
                        >
                          View Evidence →
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="p-4 text-sm max-w-[85%] border-l-4 bg-gray-100 border-gray-400 text-gray-500 italic">
                      Retrieving verified sources...
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="p-4 bg-white border-t border-gray-200">
            {messages.length > 0 && !isLoading && (
              <div className="max-w-3xl mx-auto flex flex-wrap gap-2 mb-3">
                <button 
                  onClick={() => setInput("What certification do I need?")}
                  className="bg-gray-50 border border-gray-300 text-xs text-gray-600 px-3 py-1.5 rounded-sm hover:border-blue-500 hover:text-blue-700 transition-colors"
                >
                  What certification do I need?
                </button>
                <button 
                  onClick={() => setInput("What testing is required?")}
                  className="bg-gray-50 border border-gray-300 text-xs text-gray-600 px-3 py-1.5 rounded-sm hover:border-blue-500 hover:text-blue-700 transition-colors"
                >
                  What testing is required?
                </button>
                <button 
                  onClick={() => setInput("Find relevant testing laboratories")}
                  className="bg-gray-50 border border-gray-300 text-xs text-gray-600 px-3 py-1.5 rounded-sm hover:border-blue-500 hover:text-blue-700 transition-colors"
                >
                  Find relevant testing laboratories
                </button>
              </div>
            )}
            <form onSubmit={handleSend} className="max-w-3xl mx-auto flex gap-2">
              <input
                type="text"
                className="flex-1 p-3 border border-gray-300 bg-gray-50 focus:bg-white text-sm focus:ring-1 focus:ring-blue-600 outline-none transition-colors"
                placeholder="Enter technical query..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button 
                type="submit" 
                className="bg-blue-700 text-white px-6 py-3 text-sm font-medium hover:bg-blue-800 transition-colors"
              >
                Submit
              </button>
            </form>
          </div>
        </div>

        {/* Evidence Rail */}
        <div className="w-96 border-l border-gray-200 bg-white flex flex-col h-full overflow-y-auto">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider">Evidence Rail</h2>
          </div>
          <div className="p-4 flex-1">
            {activeCitations.length === 0 ? (
              <p className="text-sm text-gray-500 text-center mt-10">No active evidence to display. Submit a query to retrieve source documentation.</p>
            ) : (
              <div className="space-y-6">
                {activeCitations.map((cit, idx) => (
                  <EvidenceRail key={idx} citation={cit} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
