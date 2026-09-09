import React, { useRef, useState } from 'react';
import { CalendarDays } from 'lucide-react';
import { displayToNativeDate, nativeToDisplayDate, normalizeDate } from '../../features/complaint/dateUtils';

function ComplaintField({ definition, value, onChange, isHighlighted, isMissing, readOnly }) {
  const { label, type = 'text', placeholder = 'Awaiting AI extraction...', options = [], wide } = definition;
  const dateInputRef = useRef(null);
  const [dateError, setDateError] = useState(false);

  const handleDateTextChange = (event) => {
    setDateError(false);
    onChange(event.target.value);
  };

  const handleDateBlur = () => {
    if (!value) return;
    const normalized = normalizeDate(value);
    setDateError(!normalized);
    if (normalized) onChange(normalized);
    else onChange('');
  };

  const handleDatePickerChange = (event) => {
    setDateError(false);
    onChange(nativeToDisplayDate(event.target.value));
  };

  const openDatePicker = () => {
    if (dateInputRef.current?.showPicker) dateInputRef.current.showPicker();
    else dateInputRef.current?.click();
  };

  return (
    <label className={`field ${wide ? 'field-wide' : ''} ${isHighlighted ? 'field-ai-highlight' : ''} ${isMissing ? 'field-missing' : ''} ${dateError ? 'field-error' : ''}`}>
      <span>{label}</span>
      <div className="field-control">
        {type === 'date' ? (
          <>
            <input type="text" inputMode="numeric" value={value} placeholder="DD/MM/YYYY" onChange={handleDateTextChange} onBlur={handleDateBlur} readOnly={readOnly} />
            <button type="button" className="date-picker-button" onClick={openDatePicker} aria-label={`Choose ${label}`}><CalendarDays size={15} /></button>
            <input ref={dateInputRef} className="native-date-picker" type="date" value={displayToNativeDate(value)} onChange={handleDatePickerChange} tabIndex={-1} aria-hidden="true" />
          </>
        ) : type === 'select' ? (
          <select value={value} onChange={(event) => onChange(event.target.value)} disabled={readOnly}>
            <option value="">{placeholder}</option>
            {options.map((option) => <option key={option}>{option}</option>)}
          </select>
        ) : type === 'textarea' ? (
          <textarea value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} readOnly={readOnly} />
        ) : (
          <input type={type} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} readOnly={readOnly} />
        )}
      </div>
      {dateError && <small className="field-error-text">Use a valid date in DD/MM/YYYY format.</small>}
    </label>
  );
}

export default ComplaintField;
