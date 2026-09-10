const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function getApiHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) throw new Error(`Health check failed with status ${response.status}`);
  return response.json();
}

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

export async function intakeComplaintFile(file, existingComplaint) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('existingComplaint', JSON.stringify(existingComplaint));

  const response = await fetch(`${API_BASE_URL}/api/complaints/intake-file`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error(`Complaint file intake failed with status ${response.status}`);
  }

  return response.json();
}

export async function saveComplaint(payload) {
  const response = await fetch(`${API_BASE_URL}/api/complaints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Complaint save failed with status ${response.status}`);
  }

  return response.json();
}

export async function listComplaints() {
  const response = await fetch(`${API_BASE_URL}/api/complaints`);
  if (!response.ok) throw new Error(`Complaint list failed with status ${response.status}`);
  return response.json();
}

export async function deleteComplaint(id) {
  const response = await fetch(`${API_BASE_URL}/api/complaints/${id}`, {
    method: 'DELETE'
  });

  if (!response.ok) {
    throw new Error(`Complaint deletion failed with status ${response.status}`);
  }

  return response.json();
}
