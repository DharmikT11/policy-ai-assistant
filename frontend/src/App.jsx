import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

// CHECK THIS LINE CAREFULLY: Ensure 'Download' is in the list
import { 
  Bot, Send, UploadCloud, FileText, ArrowLeft, 
  Sparkles, CheckCircle2, User, Copy, Check, 
  Trash2, AlertCircle, Download  // <--- ADD THIS
} from 'lucide-react';

import './App.css';

const api = axios.create({ baseURL: 'http://localhost:8000' });

function App() {
  const [view, setView] = useState('landing');
  const [companyId] = useState(`comp_${Math.random().toString(36).substr(2, 9)}`);
  
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  
  const messagesEndRef = useRef(null);

  const quickActions = [
    "Summarize this policy",
    "List all holidays",
    "What is the notice period?"
  ];

  const handleUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setUploadStatus('uploading');
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('company_id', companyId);

    try {
      await api.post('/upload', formData);
      setFile(selectedFile);
      setUploadStatus('success');
      
      setTimeout(() => {
        setView('workspace');
        setMessages([{ 
          role: 'assistant', 
          text: `**${selectedFile.name}** is active. Ask me anything about the policy!`,
          timestamp: new Date()
        }]);
      }, 1000);

    } catch (error) {
      console.error(error);
      setUploadStatus('error');
    }
  };

  const sendMessage = async (text) => {
    if (!text) return;
    const msgText = typeof text === 'string' ? text : input;
    
    if (!msgText.trim()) return;

    setMessages(prev => [...prev, { role: 'user', text: msgText }]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await api.post('/chat', { question: msgText, company_id: companyId });
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: res.data.answer,
        sources: res.data.sources 
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: "Server error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadChat = () => {
    const textContent = messages.map(m => `[${m.role.toUpperCase()}]: ${m.text}`).join('\n\n');
    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat-history.txt';
    a.click();
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const resetSession = () => {
    setView('landing');
    setFile(null);
    setMessages([]);
    setUploadStatus('idle');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // VIEW 1: LANDING
  if (view === 'landing') {
    return (
      <div className="landing-container">
        <div className="hero-card">
          <div className="hero-icon"><Bot size={40} /></div>
          <h1 className="hero-title">Policy AI Assistant</h1>
          <p className="hero-subtitle">Upload your HR Policy document to get instant answers.</p>

          <label className="landing-upload">
            <input type="file" onChange={handleUpload} accept=".pdf,.docx,.txt" hidden />
            {uploadStatus === 'idle' && (
              <div style={{display:'flex', flexDirection:'column', alignItems:'center', gap: 10}}>
                <UploadCloud size={40} color="#6366f1" />
                <span style={{fontWeight:600}}>Click to Upload</span>
                <span style={{fontSize:'0.8rem', color:'#64748b'}}>PDF, DOCX, TXT</span>
              </div>
            )}
            {uploadStatus === 'uploading' && <div style={{color:'#6366f1'}}>⚡ Analyzing...</div>}
            {uploadStatus === 'success' && <div style={{color:'#10b981'}}>✅ Ready! Entering...</div>}
          </label>
        </div>
      </div>
    );
  }

  // VIEW 2: WORKSPACE
  return (
    <div className="workspace-container">
      {/* SIDEBAR */}
      <aside className="mini-sidebar">
        <div>
          <h3 style={{margin:'0 0 20px 0', fontSize:'1rem', fontWeight:600}}>Active Session</h3>
          <div className="file-info-card">
            <FileText size={20} color="#6366f1" />
            <div style={{overflow:'hidden'}}>
              <div className="file-name">{file?.name}</div>
              <div className="live-badge">● Live</div>
            </div>
          </div>

          <div style={{marginTop: 30}}>
            <h4 style={{fontSize:'0.75rem', color:'#94a3b8', marginBottom:10, textTransform:'uppercase'}}>Quick Actions</h4>
            {quickActions.map((action, i) => (
              <button key={i} className="quick-btn" onClick={() => sendMessage(action)}>
                <Sparkles size={14} color="#6366f1" />
                {action}
              </button>
            ))}
          </div>
        </div>

        <button onClick={resetSession} className="back-btn">
          <ArrowLeft size={16} /> Upload New File
        </button>
      </aside>

      {/* CHAT MAIN */}
      <main className="chat-main">
        <header className="chat-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Bot size={24} color="#6366f1" />
            <span style={{ fontWeight: 600, color: '#334155' }}>AI Policy Agent</span>
          </div>
          
          {/* HEADER ACTIONS (DOWNLOAD) */}
          <div style={{display:'flex', gap: 10}}>
            <button className="header-btn" onClick={downloadChat} title="Download Chat">
              <Download size={20} />
            </button>
          </div>
        </header>

        <div className="messages-scroll">
          {messages.map((msg, i) => (
            <div key={i} className={`message-row ${msg.role === 'user' ? 'user' : 'ai'}`}>
              {msg.role === 'assistant' && (
                <div className="msg-avatar ai-av"><Bot size={20} /></div>
              )}

              <div style={{display:'flex', flexDirection:'column', maxWidth:'75%'}}>
                <div className={`msg-bubble ${msg.role === 'user' ? 'user-bub' : 'ai-bub'}`}>
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
                
                {/* Copy Button for AI */}
                {msg.role === 'assistant' && (
                  <div style={{marginTop: 5}}>
                    <button 
                      onClick={() => copyToClipboard(msg.text, i)}
                      style={{border:'none', background:'transparent', color:'#94a3b8', fontSize:'0.75rem', cursor:'pointer', display:'flex', alignItems:'center', gap:4}}
                    >
                      {copiedIndex === i ? <Check size={12}/> : <Copy size={12}/>}
                      {copiedIndex === i ? "Copied" : "Copy"}
                    </button>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="msg-avatar user-av"><User size={20} /></div>
              )}
            </div>
          ))}
          
          {isLoading && (
             <div className="message-row ai">
               <div className="msg-avatar ai-av"><Bot size={20} /></div>
               <div className="msg-bubble ai-bub" style={{color:'#94a3b8'}}>Thinking...</div>
             </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-wrapper">
          <form className="chat-input-box" onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}>
            <input 
              value={input} 
              onChange={e => setInput(e.target.value)}
              placeholder="Ask a question or request a draft..." 
              autoFocus
            />
            <button type="submit" className="btn-send" disabled={isLoading}>
              <Send size={18} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;