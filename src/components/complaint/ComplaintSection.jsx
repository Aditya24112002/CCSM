import React from 'react';
import ComplaintField from './ComplaintField';

function ComplaintSection({ title, fields, values, onChange, highlightedFields, missingFields }) {
  return (
    <section className="form-section">
      <h3>{title}</h3>
      <div className="fields-grid">
        {fields.map((field) => (
          <ComplaintField
            key={field.name}
            definition={field}
            value={values[field.name]}
          onChange={(value) => onChange(field.name, value)}
          isHighlighted={highlightedFields.includes(field.name)}
          isMissing={missingFields.includes(field.name)}
          readOnly={field.readOnly}
          />
        ))}
      </div>
    </section>
  );
}

export default ComplaintSection;
