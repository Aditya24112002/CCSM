import React from 'react';
import { ShieldCheck } from 'lucide-react';

function AiAssessment({ assessment }) {
  return (
    <section className="ai-assessment" aria-labelledby="ai-assessment-title">
      <h3 id="ai-assessment-title"><ShieldCheck size={18} /> AI Copilot risk assessment</h3>
      <div className="assessment-grid">
        <label><span>Severity (Suggested)</span><input value={assessment.severity} readOnly placeholder="Awaiting AI assessment..." /></label>
        <label><span>Suggested Next Action</span><input value={assessment.suggestedNextAction} readOnly placeholder="Awaiting AI recommendation..." /></label>
        <label className="assessment-wide"><span>Initial Risk Assessment</span><textarea value={assessment.initialRiskAssessment} readOnly placeholder="Awaiting AI risk assessment..." /></label>
      </div>
    </section>
  );
}

export default AiAssessment;
