import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Check,
  Database,
  FlaskConical,
  Info,
  MessageSquarePlus,
  PanelRightClose,
  PanelRightOpen,
  Paperclip,
  RotateCcw,
  Send,
  Sparkles,
  Moon,
  Sun,
  UploadCloud,
} from 'lucide-react';
import { resetComplaint, updateComplaint } from './store';
import ComplaintForm from './components/complaint/ComplaintForm';
import AiAssessment from './components/complaint/AiAssessment';
import SavedComplaintsViewer from './components/complaint/SavedComplaintsViewer';
import { complaintSections } from './features/complaint/complaintConfig';
import {
  deleteComplaint,
  getApiHealth,
  intakeComplaint,
  intakeComplaintFile,
  listComplaints,
  saveComplaint,
} from './services/complaintApi';

const sampleComplaint = {
  source: 'Pharmacy',
  customerName: 'Apollo Pharmacy',
  productName: 'Amoxicillin Capsules',
  strength: '500 mg',
  batchNumber: 'AMX240602',
  manufacturingDate: '01/03/2026',
  expiryDate: '28/02/2028',
  quantity: '12 capsules',
  complaintCategory: 'Product Quality Issue',
  complaintDate: '18/06/2026',
  description: 'Customer reported discolored capsules in a pack of Amoxicillin Capsules 500 mg.',
};

const emptyAssessment = {
  severity: '',
  suggestedNextAction: '',
  initialRiskAssessment: '',
};

const demoAssessment = {
  severity: 'Major',
  suggestedNextAction: 'Initiate Quality Investigation and perform batch review.',
  initialRiskAssessment:
    'Potential product quality concern identified. Review the affected complaint details and batch.',
};

function getFallbackAssessment(text) {
  if (!/product|batch|defect|discolor|damaged|broken|leak|quality/i.test(text)) {
    return {
      severity: 'Minor',
      suggestedNextAction: 'Request additional complaint details before further assessment.',
      initialRiskAssessment:
        'Limited information was provided. Clarify the complaint before determining broader product or batch impact.',
    };
  }
  return demoAssessment;
}

const fieldLabels = Object.fromEntries(
  complaintSections.flatMap((section) => section.fields.map((field) => [field.name, field.label]))
);

function getStatusClass(status) {
  const normalizedStatus = status.toLowerCase();
  if (normalizedStatus.includes('fail')) return 'status-error';
  if (normalizedStatus.includes('review') || normalizedStatus.includes('loaded'))
    return 'status-review';
  if (normalizedStatus.includes('saved') || normalizedStatus.includes('complete'))
    return 'status-success';
  return 'status-pending';
}

function App() {
  const dispatch = useDispatch();
  const complaint = useSelector((state) => state.complaint);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('Pending Triage');
  const [copilotOpen, setCopilotOpen] = useState(
    () => window.localStorage.getItem('aivoa-copilot-open') !== 'false'
  );
  const [highlightedFields, setHighlightedFields] = useState([]);
  const [extractedFields, setExtractedFields] = useState([]);
  const [sourceFile, setSourceFile] = useState('');
  const [uploadState, setUploadState] = useState('idle');
  const [missingFields, setMissingFields] = useState([]);
  const [aiMode, setAiMode] = useState('demo');
  const [extractionState, setExtractionState] = useState('idle');
  const [assessment, setAssessment] = useState(emptyAssessment);
  const [isSaving, setIsSaving] = useState(false);
  const [savedRecords, setSavedRecords] = useState([]);
  const [savedViewerOpen, setSavedViewerOpen] = useState(false);
  const [isLoadingSaved, setIsLoadingSaved] = useState(false);
  const [theme, setTheme] = useState(() => window.localStorage.getItem('aivoa-theme') || 'light');
  const fileInputRef = React.useRef(null);
  const isStarted = Boolean(messages.length);

  useEffect(() => {
    window.localStorage.setItem('aivoa-copilot-open', String(copilotOpen));
  }, [copilotOpen]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', theme === 'dark' ? '#111827' : '#f7f9fc');
    window.localStorage.setItem('aivoa-theme', theme);
  }, [theme]);

  useEffect(() => {
    getApiHealth()
      .then((health) => {
        // A configured key is not enough to claim Live mode. A successful
        // extraction response below is what promotes the indicator to green.
        if (health.mode !== 'langgraph-groq') setAiMode('demo');
      })
      .catch(() => setAiMode('demo'));
  }, []);

  const updateField = (field, value) => dispatch(updateComplaint({ [field]: value }));

  const handleSaveComplaint = async () => {
    if (extractionState !== 'complete') {
      setStatus('Complete an extraction first');
      return;
    }
    setIsSaving(true);
    try {
      const savedRecord = await saveComplaint({
        complaint,
        riskAssessment: assessment,
        originalText: messages
          .filter((item) => item.role === 'user')
          .map((item) => item.text)
          .join('\n\n'),
        sourceFile,
        mode: aiMode === 'live' ? 'langgraph-groq' : 'demo',
        changedFields: extractedFields,
        missingFields,
      });
      setStatus(savedRecord.duplicate ? 'Already Saved' : 'Saved to Local QMS');
    } catch (error) {
      console.warn('Complaint save failed.', error);
      setStatus('Save Failed');
    } finally {
      setIsSaving(false);
    }
  };

  const openSavedViewer = async () => {
    setSavedViewerOpen(true);
    setIsLoadingSaved(true);
    try {
      setSavedRecords(await listComplaints());
    } catch (error) {
      console.warn('Saved complaint records could not be loaded.', error);
      setSavedRecords([]);
    } finally {
      setIsLoadingSaved(false);
    }
  };

  const openSavedRecord = (record) => {
    dispatch(updateComplaint(record.complaint));
    setAssessment(record.riskAssessment);
    setMissingFields(record.missingFields || []);
    setExtractedFields(record.changedFields || []);
    setHighlightedFields(record.changedFields || []);
    setExtractionState('complete');
    setStatus('Saved Record Loaded');
    setSavedViewerOpen(false);
  };

  const deleteSavedRecord = async (record) => {
    if (!window.confirm(`Delete complaint record #${record.id}? This cannot be undone.`)) return;
    try {
      await deleteComplaint(record.id);
      setSavedRecords((currentRecords) => currentRecords.filter((item) => item.id !== record.id));
    } catch (error) {
      console.warn('Saved complaint could not be deleted.', error);
      window.alert('The complaint could not be deleted. Please try again.');
    }
  };

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
    setExtractionState('processing');
    setMessages((current) => [...current, { role: 'user', text: trimmed }]);
    setMessage('');
    try {
      const result = await intakeComplaint({
        message: trimmed,
        sourceFile: extractionSource,
        existingComplaint: complaint,
      });
      const extractedComplaint = result.complaint || {};
      const changedFields = result.changedFields?.length
        ? result.changedFields
        : Object.keys(extractedComplaint).filter((field) => extractedComplaint[field]);
      dispatch(updateComplaint(extractedComplaint));
      markAiFields(changedFields);
      setExtractedFields(changedFields);
      setMissingFields(
        result.missingFields ||
          Object.keys(extractedComplaint).filter((field) => !extractedComplaint[field])
      );
      setExtractionState('complete');
      setAssessment(result.riskAssessment || emptyAssessment);
      setAiMode(result.mode === 'langgraph-groq' ? 'live' : 'demo');
      setStatus('Ready to Review');
      if (extractionSource) setUploadState('success');
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text:
            result.mode === 'demo'
              ? 'Extraction completed in Demo mode. I populated the fields I could identify and generated an initial risk assessment.'
              : 'Extraction completed with the live AI service. I populated the complaint fields and generated an initial risk assessment.',
          sourceFile: result.sourceFile || extractionSource,
        },
      ]);
      return;
    } catch (error) {
      console.warn('FastAPI intake unavailable; using local demo fallback.', error);
      setAiMode('demo');
    }

    window.setTimeout(() => {
      const lower = trimmed.toLowerCase();
      const isEdit = /\b(?:sorry|actually|update|updated|correct|change|replace)\b/i.test(lower);
      if (isEdit) {
        const patch = {};
        const batchMatch = trimmed.match(/batch(?: number)?\s*(?:is|:)?\s*([\w-]+)/i);
        const quantityMatch = trimmed.match(
          /(?:quantity|affected quantity)\s*(?:is|:)?\s*([\w ]+)/i
        );
        if (batchMatch) patch.batchNumber = batchMatch[1];
        if (quantityMatch) patch.quantity = quantityMatch[1].replace(/[.]+$/, '').trim();
        if (Object.keys(patch).length) {
          dispatch(updateComplaint(patch));
          markAiFields(Object.keys(patch));
          setExtractedFields(Object.keys(patch));
        }
        setMissingFields(
          Object.keys(complaint).filter((field) => !complaint[field] && !patch[field])
        );
      } else {
        dispatch(updateComplaint(sampleComplaint));
        markAiFields(Object.keys(sampleComplaint));
        setExtractedFields(Object.keys(sampleComplaint));
        setMissingFields(Object.keys(sampleComplaint).filter((field) => !sampleComplaint[field]));
      }
      setAssessment(getFallbackAssessment(trimmed));
      setStatus('Ready to Review');
      setExtractionState('complete');
      if (extractionSource) setUploadState('success');
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: isEdit
            ? 'I updated the complaint form and preserved the remaining information.'
            : 'Complaint parsed successfully. I extracted the product details and generated an initial risk assessment.',
          sourceFile: extractionSource,
        },
      ]);
    }, 500);
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setUploadState('processing');
    setSourceFile(file.name);
    setMessages((current) => [
      ...current,
      {
        role: 'user',
        text: `Extract complaint details from "${file.name}"`,
        sourceFile: file.name,
      },
    ]);
    try {
      const result = await intakeComplaintFile(file, complaint);
      dispatch(updateComplaint(result.complaint || {}));
      markAiFields(result.changedFields || Object.keys(result.complaint || {}));
      setExtractedFields(result.changedFields || Object.keys(result.complaint || {}));
      setMissingFields(
        result.missingFields ||
          Object.keys(result.complaint || {}).filter((field) => !result.complaint[field])
      );
      setExtractionState('complete');
      setAssessment(result.riskAssessment || emptyAssessment);
      setAiMode(result.mode === 'langgraph-groq' ? 'live' : 'demo');
      setStatus('Ready to Review');
      setUploadState('success');
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: 'Complaint document parsed successfully. I extracted the available complaint details and generated an initial risk assessment.',
          sourceFile: result.sourceFile || file.name,
        },
      ]);
    } catch (error) {
      console.warn('FastAPI file intake unavailable; using local demo fallback.', error);
      setAiMode('demo');
      submitMessage(`Extract complaint details from "${file.name}"`, { sourceFile: file.name });
    }
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
    if (
      messages.length &&
      !window.confirm(
        'Closing this chat will permanently remove the current conversation history. Do you want to continue?'
      )
    )
      return;
    setMessages([]);
    setMessage('');
    setSourceFile('');
    setUploadState('idle');
    setExtractionState('idle');
    setMissingFields([]);
    setExtractedFields([]);
    setAssessment(emptyAssessment);
  };

  return (
    <main className={`app-shell ${copilotOpen ? '' : 'copilot-collapsed'}`}>
      <section className="form-panel">
        <header className="page-header">
          <div>
            <p className="eyebrow">
              <FlaskConical size={14} /> AIVOA QUALITY SYSTEM
            </p>
            <h1>Log Customer Complaint</h1>
            <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
          </div>
          <div className="page-header-actions">
            <button className="button button-secondary" onClick={openSavedViewer}>
              <Database size={15} /> Saved Complaints
            </button>
            <span className={`status-pill ${getStatusClass(status)}`}>
              <span />
              {status}
            </span>
            <button
              className="icon-button theme-toggle"
              onClick={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
        </header>

        {savedViewerOpen ? (
          <SavedComplaintsViewer
            records={savedRecords}
            isLoading={isLoadingSaved}
            onBack={() => setSavedViewerOpen(false)}
            onOpen={openSavedRecord}
            onDelete={deleteSavedRecord}
          />
        ) : (
          <>
            <ComplaintForm
              sections={complaintSections}
              complaint={complaint}
              onChange={updateField}
              highlightedFields={highlightedFields}
              missingFields={missingFields}
            />
            <AiAssessment assessment={assessment} />
            <div className="form-actions">
              <button
                className="button button-secondary"
                onClick={() => {
                  dispatch(resetComplaint());
                  setStatus('Pending Triage');
                  setHighlightedFields([]);
                  setMissingFields([]);
                  setExtractedFields([]);
                  setExtractionState('idle');
                  setAssessment(emptyAssessment);
                }}
              >
                <RotateCcw size={15} /> Reset Form
              </button>
              <button
                className="button button-primary"
                onClick={handleSaveComplaint}
                disabled={isSaving}
              >
                <Check size={15} /> {isSaving ? 'Saving...' : 'Save Complaint'}
              </button>
            </div>
          </>
        )}
      </section>

      {!copilotOpen && (
        <button
          className="copilot-fab"
          onClick={() => setCopilotOpen(true)}
          aria-label="Open AIVOA Copilot"
        >
          <PanelRightOpen size={18} />
          <span>Copilot</span>
        </button>
      )}
      <aside className="copilot-panel">
        <header className="copilot-header">
          <div className="copilot-title">
            <span className="copilot-icon">
              <FlaskConical size={18} />
            </span>
            <div>
              <h2>
                AIVOA Copilot <span>BETA</span>
              </h2>
              <p>AI-powered complaint intake assistant</p>
            </div>
          </div>
          <div className="copilot-header-actions">
            <span
              className={`online-dot ${aiMode}`}
              title={
                aiMode === 'live' ? 'Live Groq AI connected' : 'Demo mode: local fallback active'
              }
              aria-label={aiMode === 'live' ? 'Live Groq AI connected' : 'Demo mode'}
            />
            <button className="icon-button" onClick={startNewChat} aria-label="Start a new chat">
              <MessageSquarePlus size={16} />
            </button>
            <button
              className="icon-button"
              onClick={() => setCopilotOpen(false)}
              aria-label="Collapse AIVOA Copilot"
            >
              <PanelRightClose size={17} />
            </button>
          </div>
        </header>
        <div className="copilot-body">
          <div className="assistant-message welcome">
            <div className="message-avatar">
              <Sparkles size={16} />
            </div>
            <div>
              <strong>Hello! I’m AIVOA Copilot.</strong>
              <p>
                Paste a customer email, type a complaint, or upload a PDF. I’ll extract the data,
                populate the Complaint Log, and run an initial risk assessment.
              </p>
            </div>
          </div>
          {!isStarted && (
            <div
              className={`upload-card ${uploadState === 'processing' ? 'upload-processing' : ''}`}
              onDragOver={(event) => event.preventDefault()}
              onDrop={handleDrop}
            >
              <UploadCloud size={28} />
              <strong>Drop complaint document here</strong>
              <span>
                or{' '}
                <label className="upload-link">
                  click to browse
                  <input type="file" accept=".pdf,.doc,.docx,.txt,.eml" onChange={handleFile} />
                </label>
              </span>
              <small>Supported: PDF, DOCX, TXT, EML · Max file size: 10MB</small>
            </div>
          )}
          {messages.map((item, index) => (
            <div className={`chat-row ${item.role}`} key={`${item.role}-${index}`}>
              <div className="message-avatar">
                {item.role === 'assistant' ? <Check size={16} /> : <span>U</span>}
              </div>
              <div className="chat-bubble">
                <p>{item.text}</p>
                {item.sourceFile && (
                  <span className="file-reference">
                    Extracted from: &quot;{item.sourceFile}&quot;
                  </span>
                )}
              </div>
            </div>
          ))}
          {isStarted && extractionState !== 'idle' && (
            <div className={`progress-card extraction-${extractionState}`}>
              <div>
                <span>
                  {extractionState === 'processing'
                    ? 'AI extraction in progress'
                    : 'Extraction Completed'}
                </span>
                <strong>{extractionState === 'processing' ? '...' : '100%'}</strong>
              </div>
              <div className="progress-track">
                <span style={{ width: `${extractionState === 'processing' ? 72 : 100}%` }} />
              </div>
              <p>
                {extractionState === 'processing'
                  ? 'AI is reading the complaint and running extraction passes. Form edits will not affect this progress.'
                  : 'AI extraction finished. The result is preserved while you review or edit the form.'}
              </p>
              {missingFields.length > 0 && (
                <p className="review-fields">
                  <strong>Fields requiring manual review:</strong>{' '}
                  {missingFields.map((field) => fieldLabels[field] || field).join(' · ')}
                </p>
              )}
              {sourceFile && (
                <p>
                  Source file: <span className="file-reference">&quot;{sourceFile}&quot;</span>
                </p>
              )}
            </div>
          )}
        </div>
        <div className="composer">
          <div className="composer-input">
            <button
              type="button"
              className="attachment-button"
              onClick={() => fileInputRef.current?.click()}
              aria-label="Attach complaint file"
            >
              <Paperclip size={17} />
            </button>
            <input
              ref={fileInputRef}
              className="visually-hidden-file"
              type="file"
              accept=".pdf,.doc,.docx,.txt,.eml"
              onChange={handleFile}
            />
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => event.key === 'Enter' && submitMessage()}
              placeholder="Ask anything about this complaint..."
            />
            <button onClick={() => submitMessage()} aria-label="Send message">
              <Send size={16} />
            </button>
          </div>
          <p>
            <Info size={11} /> AI responses may contain errors. Please verify information.
          </p>
        </div>
      </aside>
    </main>
  );
}

export default App;