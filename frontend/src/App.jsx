import React, { useState, useEffect, useRef } from 'react';
import { Send, Upload, Database, Brain, Loader2, MessageSquare, Trash2 } from 'lucide-react';
import { chatAPI, knowledgeAPI } from './services/api';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [knowledge, setKnowledge] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [error, setError] = useState(null);
  const [knowledgeInput, setKnowledgeInput] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (activeTab === 'knowledge') {
      loadKnowledge();
    }
  }, [activeTab]);

  const loadKnowledge = async () => {
    try {
      const data = await knowledgeAPI.list();
      setKnowledge(data.knowledge || []);
    } catch (error) {
      console.error('Error loading knowledge:', error);
      setError('Failed to load knowledge base. Make sure the backend is running.');
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await chatAPI.sendMessage(input, messages);

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        sources: response.sources || [],
        timestamp: response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to get response. Make sure the backend is running on http://localhost:8000');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please make sure the backend server is running on http://localhost:8000',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddKnowledge = async () => {
    if (!knowledgeInput.trim()) return;

    try {
      setLoading(true);
      await knowledgeAPI.add(knowledgeInput);
      setKnowledgeInput('');
      await loadKnowledge();
      setError(null);
    } catch (error) {
      console.error('Error adding knowledge:', error);
      setError('Failed to add knowledge. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      await knowledgeAPI.uploadFile(file);
      await loadKnowledge();
      setError(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setError('Failed to upload file. Make sure it\'s a text file and the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteKnowledge = async (id) => {
    try {
      await knowledgeAPI.delete(id);
      await loadKnowledge();
      setError(null);
    } catch (error) {
      console.error('Error deleting knowledge:', error);
      setError('Failed to delete knowledge');
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-linear-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur-sm border-b border-purple-500/30 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-linear-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">JARVIS</h1>
              <p className="text-xs text-purple-300">Personal AI Assistant</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
                activeTab === 'chat'
                  ? 'bg-purple-500 text-white'
                  : 'bg-white/10 text-purple-200 hover:bg-white/20'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Chat
            </button>
            <button
              onClick={() => setActiveTab('knowledge')}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
                activeTab === 'knowledge'
                  ? 'bg-purple-500 text-white'
                  : 'bg-white/10 text-purple-200 hover:bg-white/20'
              }`}
            >
              <Database className="w-4 h-4" />
              Knowledge ({knowledge.length})
            </button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500/20 border-b border-red-500/50 p-3">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <p className="text-red-200 text-sm">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-200 hover:text-white transition-colors"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? (
          <div className="h-full flex flex-col max-w-4xl mx-auto p-4">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.length === 0 && (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Brain className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Welcome to JARVIS
                    </h2>
                    <p className="text-purple-300 max-w-md mb-4">
                      Your personal AI assistant powered by self-hosted LLM and
                      vector database. Start chatting or add knowledge to enhance
                      my capabilities!
                    </p>
                    <div className="flex gap-2 justify-center">
                      <div className="bg-white/5 border border-purple-500/30 rounded-lg p-3 text-left">
                        <p className="text-purple-300 text-sm mb-1">💡 Try asking:</p>
                        <p className="text-white text-xs">"Who are you?"</p>
                        <p className="text-white text-xs">"What can you do?"</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-2xl rounded-2xl p-4 ${
                      message.role === 'user'
                        ? 'bg-linear-to-r from-purple-500 to-pink-500 text-white'
                        : 'bg-white/10 backdrop-blur-sm text-white border border-purple-500/30'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-white/20">
                        <p className="text-xs text-purple-200 mb-1 flex items-center gap-1">
                          <Database className="w-3 h-3" />
                          Used {message.sources.length} knowledge source(s)
                        </p>
                        <div className="mt-2 space-y-1">
                          {message.sources.slice(0, 2).map((source, idx) => (
                            <p key={idx} className="text-xs text-purple-300 italic">
                              "{source.substring(0, 80)}..."
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-purple-500/30">
                    <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-purple-500/30 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="Ask me anything..."
                  className="flex-1 bg-transparent text-white placeholder-purple-300 outline-none"
                  disabled={loading}
                />
                <button
                  onClick={clearChat}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  title="Clear chat"
                  disabled={loading}
                >
                  <Trash2 className="w-5 h-5 text-purple-300" />
                </button>
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="bg-linear-to-r from-purple-500 to-pink-500 text-white p-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full max-w-4xl mx-auto p-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-purple-500/30 p-6 h-full flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white">Knowledge Base</h2>
                <label className="bg-linear-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:opacity-90 transition-opacity cursor-pointer flex items-center gap-2 disabled:opacity-50">
                  <Upload className="w-4 h-4" />
                  Upload Document
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileUpload}
                    className="hidden"
                    accept=".txt,.md"
                    disabled={loading}
                  />
                </label>
              </div>

              <div className="mb-6">
                <textarea
                  value={knowledgeInput}
                  onChange={(e) => setKnowledgeInput(e.target.value)}
                  placeholder="Add knowledge manually... (Press Ctrl+Enter to save)"
                  className="w-full bg-white/5 border border-purple-500/30 rounded-lg p-3 text-white placeholder-purple-300 outline-none resize-none focus:border-purple-500/50"
                  rows="3"
                  disabled={loading}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.ctrlKey) {
                      e.preventDefault();
                      handleAddKnowledge();
                    }
                  }}
                />
                <div className="flex justify-end mt-2">
                  <button
                    onClick={handleAddKnowledge}
                    disabled={loading || !knowledgeInput.trim()}
                    className="bg-linear-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <Database className="w-4 h-4" />
                        Add Knowledge
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto space-y-3">
                {knowledge.length === 0 ? (
                  <div className="text-center py-12">
                    <Database className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                    <p className="text-purple-300 mb-2">No knowledge entries yet</p>
                    <p className="text-purple-400 text-sm">
                      Add knowledge manually or upload a document to get started!
                    </p>
                  </div>
                ) : (
                  knowledge.map((item) => (
                    <div
                      key={item.id}
                      className="bg-white/5 border border-purple-500/30 rounded-lg p-4 hover:bg-white/10 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <span className="text-xs text-purple-300">
                            {new Date(item.timestamp).toLocaleString()}
                          </span>
                          {item.metadata?.filename && (
                            <span className="text-xs text-purple-400 ml-2">
                              📄 {item.metadata.filename}
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteKnowledge(item.id)}
                          className="text-red-400 hover:text-red-300 transition-colors p-1"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-white text-sm leading-relaxed">
                        {item.text.length > 200 
                          ? `${item.text.substring(0, 200)}...` 
                          : item.text}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-black/30 backdrop-blur-sm border-t border-purple-500/30 p-3">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-xs text-purple-300">
            🧠 Self-hosted LLM • 📊 Vector Database • 💬 RAG Pipeline
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;