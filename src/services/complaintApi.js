const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function intakeComplaint(payload) {
  const response = await fetch(`${API_BASE_URL}/api/complaints/intake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Complaint intake failed with status ${response.status}`);
  }

  return response.json();
}
