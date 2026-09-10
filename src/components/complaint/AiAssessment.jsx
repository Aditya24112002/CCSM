import React from 'react';
import { ShieldCheck } from 'lucide-react';

function getSeverityClass(severity) {
  const normalizedSeverity = severity.toLowerCase();
  if (normalizedSeverity.includes('critical')) return 'critical';
  if (normalizedSeverity.includes('high') || normalizedSeverity.includes('major')) return 'high';
  if (normalizedSeverity.includes('medium') || normalizedSeverity.includes('moderate'))
    return 'medium';
  if (normalizedSeverity.includes('low') || normalizedSeverity.includes('minor')) return 'low';
  return 'unknown';
}

function AiAssessment({ assessment }) {
  return (
    <section
      className={`ai-assessment risk-${getSeverityClass(assessment.severity)}`}
      aria-labelledby="ai-assessment-title"
    >
      <h3 id="ai-assessment-title">
        <ShieldCheck size={18} />
        <span>AI Copilot risk assessment</span>
        <span className="risk-badge">{assessment.severity || 'Awaiting assessment'}</span>
      </h3>
      <div className="assessment-grid">
        <label className="assessment-severity">
          <span>Severity (Suggested)</span>
          <input value={assessment.severity} readOnly placeholder="Awaiting AI assessment..." />
        </label>
        <label>
          <span>Suggested Next Action</span>
          <input
            value={assessment.suggestedNextAction}
            readOnly
            placeholder="Awaiting AI recommendation..."
          />
        </label>
        <label className="assessment-wide">
          <span>Initial Risk Assessment</span>
          <textarea
            value={assessment.initialRiskAssessment}
            readOnly
            placeholder="Awaiting AI risk assessment..."
          />
        </label>
      </div>
    </section>
  );
}

export default AiAssessment;
