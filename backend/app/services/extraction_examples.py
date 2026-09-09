"""Curated few-shot examples for complaint extraction.

These examples guide the live model's output format and terminology. They are
prompt examples, not training data or a replacement for response validation.
"""

EXTRACTION_EXAMPLES = r'''
Use these examples as formatting and quality guidance. Do not copy their values
into a new complaint unless the new complaint contains the same facts.

Example 1 - product quality complaint
Input:
Apollo Pharmacy reported discolored Amoxicillin Capsules 500 mg from batch AMX240602. The complaint was received on 18 June 2026.
Expected output:
{
  "customerName": "Apollo Pharmacy",
  "productName": "Amoxicillin Capsules",
  "strength": "500 mg",
  "batchNumber": "AMX240602",
  "complaintCategory": "Product Quality Issue",
  "complaintDate": "18/06/2026",
  "description": "Customer reported discoloration in Amoxicillin Capsules 500 mg from batch AMX240602. The issue represents a potential product quality concern requiring further investigation.",
  "severity": "Major",
  "suggestedNextAction": "Initiate Quality Investigation and request product samples.",
  "initialRiskAssessment": "Potential product quality defect identified. The affected batch should be reviewed to determine scope and root cause."
}

Example 2 - packaging complaint
Input:
The customer found a broken seal on the blister pack of Paracetamol Tablets 500 mg, batch PCM-7788. The complaint date is 04/07/2026.
Expected output:
{
  "productName": "Paracetamol Tablets",
  "strength": "500 mg",
  "batchNumber": "PCM-7788",
  "complaintCategory": "Packaging Issue",
  "complaintDate": "04/07/2026",
  "description": "Customer reported a broken blister-pack seal affecting Paracetamol Tablets 500 mg from batch PCM-7788. The packaging defect should be investigated for potential product exposure.",
  "severity": "Minor",
  "suggestedNextAction": "Request product samples and initiate a packaging quality investigation.",
  "initialRiskAssessment": "Potential packaging integrity failure identified; assess product exposure and batch scope."
}

Example 3 - labeling complaint
Input:
A hospital reported that the outer carton displays the wrong dosage instruction for Cefixime Suspension 100 mg/5 mL. Batch CF-102 was received on 12 August 2026.
Expected output:
{
  "productName": "Cefixime Suspension",
  "strength": "100 mg/5 mL",
  "batchNumber": "CF-102",
  "complaintCategory": "Labeling Issue",
  "complaintDate": "12/08/2026",
  "description": "Hospital reported an incorrect dosage instruction on the outer carton of Cefixime Suspension 100 mg/5 mL from batch CF-102. The labeling discrepancy requires review to determine potential use-related risk.",
  "severity": "Critical",
  "suggestedNextAction": "Escalate to the QA Team and initiate an immediate labeling investigation.",
  "initialRiskAssessment": "Incorrect dosage information may create a potential use-related risk and requires urgent assessment."
}

Example 4 - explicit customer name and relative expiry
Input:
I am Ayesha Kadhra. I am complaining about product 4U-500, strength 200 milligrams, batch BTCH_2025, manufactured 24 November 2025 and expiring after one year. Today is 10/09/2026. The capsules have the wrong color and wrong size.
Expected output:
{
  "customerName": "Ayesha Kadhra",
  "productName": "4U-500",
  "strength": "200 mg",
  "batchNumber": "BTCH_2025",
  "manufacturingDate": "24/11/2025",
  "expiryDate": "24/11/2026",
  "complaintCategory": "Product Quality Issue",
  "complaintDate": "10/09/2026",
  "description": "Customer reported wrong color and wrong size in 4U-500 200 mg capsules from batch BTCH_2025. The observations represent a potential product quality concern requiring further investigation.",
  "severity": "Major",
  "suggestedNextAction": "Initiate Quality Investigation and request product samples.",
  "initialRiskAssessment": "Potential product quality defect identified; review the affected batch and samples to determine scope and root cause."
}

Example 5 - missing date
Input:
A customer reported leaking bottles of Cough Syrup 100 mL from batch CS-44. No complaint date was included.
Expected output:
{
  "productName": "Cough Syrup",
  "strength": "100 mL",
  "batchNumber": "CS-44",
  "complaintCategory": "Packaging Issue",
  "complaintDate": "CURRENT_DATE_DD/MM/YYYY",
  "description": "Customer reported leaking Cough Syrup 100 mL bottles from batch CS-44. The packaging issue requires investigation to assess product integrity and affected batch scope.",
  "severity": "Major",
  "suggestedNextAction": "Request product samples and initiate a packaging quality investigation.",
  "initialRiskAssessment": "Potential container-closure failure identified; assess product integrity and batch impact."
}

Example 6 - incomplete complaint
Input:
The product packaging appears damaged.
Expected output:
{
  "complaintCategory": "Packaging Issue",
  "complaintDate": "CURRENT_DATE_DD/MM/YYYY",
  "description": "Customer reported apparent damage to the product packaging. Further details are required to identify the product, batch, and potential impact.",
  "severity": "Minor",
  "suggestedNextAction": "Request product samples and additional complaint details.",
  "initialRiskAssessment": "Insufficient information is available for a complete risk determination; packaging impact requires review."
}

Example 7 - correction message
Input:
Correction: the batch number is AMX240603, not AMX240602. The product is Amoxicillin Capsules and the strength is 500 mg.
Expected output:
{
  "productName": "Amoxicillin Capsules",
  "strength": "500 mg",
  "batchNumber": "AMX240603"
}

Example 8 - correction message
Input:
Correction: the manufacturing date was entered incorrectly. It should be April 2026, not March 2026.
Expected output:
{
  "manufacturingDate": null
}

Example 9 – Expiry Date Correction
Input:
Update: the expiry date is January 2029, not February 2028.
Expected Output:
{
  "expiryDate": null
}


'''
