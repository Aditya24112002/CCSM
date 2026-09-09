import React from 'react';
import ComplaintSection from './ComplaintSection';

function ComplaintForm({ sections, complaint, onChange, highlightedFields = [], missingFields = [] }) {
  return (
    <div className="form-content">
      {sections.map((section) => (
        <ComplaintSection
          key={section.title}
          title={section.title}
          fields={section.fields}
          values={complaint}
          onChange={onChange}
          highlightedFields={highlightedFields}
          missingFields={missingFields}
        />
      ))}
    </div>
  );
}

export default ComplaintForm;
