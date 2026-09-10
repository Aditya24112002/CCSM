import { configureStore, createSlice } from '@reduxjs/toolkit';

export const initialComplaint = {
  source: '',
  customerName: '',
  productName: '',
  strength: '',
  batchNumber: '',
  manufacturingDate: '',
  expiryDate: '',
  quantity: '',
  complaintCategory: '',
  complaintDate: '',
  description: '',
};

const complaintSlice = createSlice({
  name: 'complaint',
  initialState: initialComplaint,
  reducers: {
    updateComplaint: (state, action) => ({ ...state, ...action.payload }),
    resetComplaint: () => initialComplaint,
  },
});

export const { updateComplaint, resetComplaint } = complaintSlice.actions;
export const store = configureStore({ reducer: { complaint: complaintSlice.reducer } });
