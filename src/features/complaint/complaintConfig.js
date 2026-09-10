export const complaintSections = [
  {
    title: '1. Origin & Customer Details',
    fields: [
      { name: 'source', label: 'Complaint Source', type: 'text' },
      { name: 'customerName', label: 'Customer Name', type: 'text' },
    ],
  },
  {
    title: '2. Product & Batch Identification',
    fields: [
      { name: 'productName', label: 'Product Name', type: 'text' },
      { name: 'strength', label: 'Product Strength / Grade', type: 'text' },
      { name: 'batchNumber', label: 'Batch / Lot Number', type: 'text' },
      { name: 'manufacturingDate', label: 'Manufacturing Date', type: 'date' },
      { name: 'expiryDate', label: 'Expiry Date', type: 'date' },
      { name: 'quantity', label: 'Quantity Affected', type: 'text' },
    ],
  },
  {
    title: '3. Complaint Details',
    fields: [
      {
        name: 'complaintCategory',
        label: 'Complaint Category',
        type: 'text',
        readOnly: true,
        placeholder: 'Awaiting AI classification...',
      },
      { name: 'complaintDate', label: 'Complaint Date', type: 'date' },
      {
        name: 'description',
        label: 'Detailed Complaint Description',
        type: 'textarea',
        wide: true,
      },
    ],
  },
];
