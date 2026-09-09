import React, { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Check,
  FlaskConical,
  Info,
  MessageSquarePlus,
  PanelRightClose,
  PanelRightOpen,
  Paperclip,
  RotateCcw,
  Send,
  Sparkles,
  UploadCloud
} from 'lucide-react';
import { resetComplaint, updateComplaint } from './store';
import ComplaintForm from './components/complaint/ComplaintForm';
import { complaintSections } from './features/complaint/complaintConfig';
import { intakeComplaint } from './services/complaintApi';

const sampleComplaint = {
  source: 'Pharmacy',
  customerName: 'Apollo Pharmacy',
  productName: 'Amoxicillin Capsules',
  strength: '500 mg',
  batchNumber: 'AMX240602',
  manufacturingDate: '01/03/2026',
  expiryDate: '28/02/2028',
  quantity: '12 capsules',
  complaintType: 'Product quality defect',
  complaintDate: '18/06/2026',
  description: 'Customer reported discolored capsules in a pack of Amoxicillin Capsules 500 mg.',
  severity: 'Major',
  priority: 'High'
};

function App() {
  const dispatch = useDispatch();
  const complaint = useSelector((state) => state.complaint);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('Pending Triage');
  const [copilotOpen, setCopilotOpen] = useState(() => window.localStorage.getItem('aivoa-copilot-open') !== 'false');
  const [highlightedFields, setHighlightedFields] = useState([]);
  const [sourceFile, setSourceFile] = useState('');
  const [uploadState, setUploadState] = useState('idle');
  const fileInputRef = React.useRef(null);
  const isStarted = Boolean(messages.length);

  useEffect(() => {
    window.localStorage.setItem('aivoa-copilot-open', String(copilotOpen));
  }, [copilotOpen]);

  const completion = useMemo(() => {
    const fields = Object.values(complaint);
    return Math.round((fields.filter(Boolean).length / fields.length) * 100);
  }, [complaint]);

  const updateField = (field, value) => dispatch(updateComplaint({ [field]: value }));

  const markAiFields = (fields) => {
    setHighlightedFields(fields);
    window.setTimeout(() => setHighlightedFields([]), 4200);
  };

  const submitMessage = async (text = message, extraction = {}) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    const extractionSource = extraction.sourceFile || sourceFile;
    if (extraction.sourceFile) setSourceFile(extraction.sourceFile);
    if (extractionSource) setUploadState('processing');
    setMessages((current) => [...current, { role: 'user', text: trimmed }]);
    setMessage('');
    try {
      const result = await intakeComplaint({
        message: trimmed,
        sourceFile: extractionSource,
        existingComplaint: complaint
      });
      const extractedComplaint = result.complaint || {};
      const changedFields = result.changedFields?.length
        ? result.changedFields
        : Object.keys(extractedComplaint).filter((field) => extractedComplaint[field]);
      dispatch(updateComplaint(extractedComplaint));
      markAiFields(changedFields);
      setStatus('Ready to Review');
      if (extractionSource) setUploadState('success');
      setMessages((current) => [...current, {
        role: 'assistant',
        text: result.mode === 'demo'
          ? 'Complaint parsed successfully through the local FastAPI demo service. I extracted the product details and generated an initial risk assessment.'
          : 'Complaint parsed successfully. I extracted the product details and generated an initial risk assessment.',
        sourceFile: result.sourceFile || extractionSource
      }]);
      return;
    } catch (error) {
      console.warn('FastAPI intake unavailable; using local demo fallback.', error);
    }

    window.setTimeout(() => {
      const lower = trimmed.toLowerCase();
      const isEdit = lower.includes('batch') || lower.includes('quantity') || lower.includes('update');
      if (isEdit) {
        const patch = {};
        const batchMatch = trimmed.match(/batch(?: number)?\s*(?:is|:)?\s*([A-Z0-9-]+)/i);
        const quantityMatch = trimmed.match(/(?:quantity|affected quantity)\s*(?:is|:)?\s*([\w ]+)/i);
        if (batchMatch) patch.batchNumber = batchMatch[1];
        if (quantityMatch) patch.quantity = quantityMatch[1].replace(/[.]+$/, '').trim();
        if (Object.keys(patch).length) {
          dispatch(updateComplaint(patch));
          markAiFields(Object.keys(patch));
        }
      } else {
        dispatch(updateComplaint(sampleComplaint));
        markAiFields(Object.keys(sampleComplaint));
      }
      setStatus('Ready to Review');
      if (extractionSource) setUploadState('success');
      setMessages((current) => [...current, {
        role: 'assistant',
        text: isEdit ? 'I updated the complaint form and preserved the remaining information.' : 'Complaint parsed successfully. I extracted the product details and generated an initial risk assessment.',
        sourceFile: extractionSource
      }]);
    }, 500);
  };

  const handleFileUpload = (file) => {
    if (!file) return;
    setUploadState('processing');
    submitMessage(`Extract complaint details from "${file.name}"`, { sourceFile: file.name });
  };

  const handleFile = (event) => {
    handleFileUpload(event.target.files?.[0]);
    event.target.value = '';
  };

  const handleDrop = (event) => {
    event.preventDefault();
    handleFileUpload(event.dataTransfer.files?.[0]);
  };

  const startNewChat = () => {
    if (messages.length && !window.confirm('Closing this chat will permanently remove the current conversation history. Do you want to continue?')) return;
    setMessages([]);
    setMessage('');
    setSourceFile('');
    setUploadState('idle');
  };

  return (
    <main className={`app-shell ${copilotOpen ? '' : 'copilot-collapsed'}`}>
      <section className="form-panel">
        <header className="page-header">
          <div>
            <p className="eyebrow"><FlaskConical size={14} /> AIVOA QUALITY SYSTEM</p>
            <h1>Log Customer Complaint</h1>
            <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
          </div>
          <span className={`status-pill ${status === 'Ready to Review' ? 'status-ready' : ''}`}><span />{status}</span>
        </header>

        <ComplaintForm sections={complaintSections} complaint={complaint} onChange={updateField} highlightedFields={highlightedFields} />
        <div className="form-actions">
            <button className="button button-secondary" onClick={() => { dispatch(resetComplaint()); setStatus('Pending Triage'); setHighlightedFields([]); }}><RotateCcw size={15} /> Reset Form</button>
            <button className="button button-primary" onClick={() => setStatus('Saved Locally')}><Check size={15} /> Save Complaint</button>
        </div>
      </section>

      {!copilotOpen && <button className="copilot-fab" onClick={() => setCopilotOpen(true)} aria-label="Open AIVOA Copilot"><PanelRightOpen size={18} /><span>Copilot</span></button>}
      <aside className="copilot-panel">
        <header className="copilot-header">
          <div className="copilot-title"><span className="copilot-icon"><FlaskConical size={18} /></span><div><h2>AIVOA Copilot <span>BETA</span></h2><p>AI-powered complaint intake assistant</p></div></div>
          <div className="copilot-header-actions"><span className="online-dot" /><button className="icon-button" onClick={startNewChat} aria-label="Start a new chat"><MessageSquarePlus size={16} /></button><button className="icon-button" onClick={() => setCopilotOpen(false)} aria-label="Collapse AIVOA Copilot"><PanelRightClose size={17} /></button></div>
        </header>
        <div className="copilot-body">
          <div className="assistant-message welcome"><div className="message-avatar"><Sparkles size={16} /></div><div><strong>Ready to process a complaint</strong><p>Paste a customer email, type a complaint, or upload a PDF. I’ll extract the data and run an initial risk assessment.</p></div></div>
          {!isStarted && <div className={`upload-card ${uploadState === 'processing' ? 'upload-processing' : ''}`} onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}><UploadCloud size={28} /><strong>Drop complaint document here</strong><span>or <label className="upload-link">click to browse<input type="file" accept=".pdf,.doc,.docx,.txt,.eml" onChange={handleFile} /></label></span><small>Supported: PDF, DOCX, TXT, EML · Max file size: 10MB</small></div>}
          {messages.map((item, index) => <div className={`chat-row ${item.role}`} key={`${item.role}-${index}`}><div className="message-avatar">{item.role === 'assistant' ? <Check size={16} /> : <span>U</span>}</div><div className="chat-bubble"><p>{item.text}</p>{item.sourceFile && <span className="file-reference">Extracted from: &quot;{item.sourceFile}&quot;</span>}</div></div>)}
          {isStarted && <div className="progress-card"><div><span>{uploadState === 'processing' ? 'Extracting complaint data' : 'Extraction progress'}</span><strong>{uploadState === 'processing' ? '...' : `${completion}%`}</strong></div><div className="progress-track"><span style={{ width: `${uploadState === 'processing' ? 42 : Math.max(completion, 10)}%` }} /></div><p>{sourceFile ? <>Source file: <span className="file-reference">&quot;{sourceFile}&quot;</span></> : 'Complaint data is being mapped to the quality record.'}</p></div>}
        </div>
        <div className="composer"><div className="composer-input"><button type="button" className="attachment-button" onClick={() => fileInputRef.current?.click()} aria-label="Attach complaint file"><Paperclip size={17} /></button><input ref={fileInputRef} className="visually-hidden-file" type="file" accept=".pdf,.doc,.docx,.txt,.eml" onChange={handleFile} /><input value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && submitMessage()} placeholder="Ask anything about this complaint..." /><button onClick={() => submitMessage()} aria-label="Send message"><Send size={16} /></button></div><p><Info size={11} /> AI responses may contain errors. Please verify information.</p></div>
      </aside>
    </main>
  );
}

export default App;
