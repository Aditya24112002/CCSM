import React from 'react';
import {
  ArrowLeft,
  CalendarDays,
  ChevronRight,
  Database,
  FileText,
  ShieldCheck,
  Trash2,
} from 'lucide-react';

function SavedComplaintsViewer({ records, isLoading, onBack, onOpen, onDelete }) {
  return (
    <section className="saved-viewer" aria-labelledby="saved-viewer-title">
      <div className="saved-viewer-header">
        <div>
          <p className="eyebrow">
            <Database size={14} /> LOCAL QMS RECORDS
          </p>
          <h2 id="saved-viewer-title">Saved Complaints</h2>
          <p>Review complaint records and their AI assessment history.</p>
        </div>
        <button className="button button-secondary" onClick={onBack}>
          <ArrowLeft size={15} /> Complaint Log
        </button>
      </div>
      {isLoading ? (
        <div className="saved-empty">Loading saved complaint records...</div>
      ) : records.length === 0 ? (
        <div className="saved-empty">
          <FileText size={24} />
          <strong>No saved complaints yet</strong>
          <span>Complete an extraction and save the complaint to create a QMS record.</span>
        </div>
      ) : (
        <div className="saved-record-list">
          {records.map((record) => (
            <article className="saved-record" key={record.id}>
              <div className="saved-record-main">
                <div className="saved-record-title">
                  <strong>{record.complaint.customerName || 'Unnamed customer'}</strong>
                  <span>Record #{record.id}</span>
                </div>
                <p>
                  {record.complaint.productName || 'Product not provided'}
                  {record.complaint.strength ? ` · ${record.complaint.strength}` : ''}
                </p>
                <div className="saved-record-meta">
                  <span>
                    <CalendarDays size={13} />{' '}
                    {record.complaint.complaintDate || 'Date unavailable'}
                  </span>
                  <span>
                    <ShieldCheck size={13} />{' '}
                    {record.riskAssessment.severity || 'Assessment unavailable'}
                  </span>
                  <span>{record.mode === 'langgraph-groq' ? 'Live AI' : 'Demo'}</span>
                </div>
              </div>
              <div className="saved-record-actions">
                <button
                  className="icon-button saved-delete-button"
                  onClick={() => onDelete(record)}
                  aria-label={`Delete complaint record ${record.id}`}
                >
                  <Trash2 size={16} />
                </button>
                <button
                  className="icon-button saved-open-button"
                  onClick={() => onOpen(record)}
                  aria-label={`Open complaint record ${record.id}`}
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default SavedComplaintsViewer;
