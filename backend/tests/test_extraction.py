import unittest
from datetime import date

from backend.app.schemas import ComplaintData, IntakeRequest
from backend.app.services.date_resolution import extract_relative_date_patch, format_local_today, resolve_date_expression
from backend.app.services.demo_extractor import extract_demo


class ComplaintExtractionTests(unittest.TestCase):
    def test_customer_name_and_source_are_split(self):
        result = extract_demo(IntakeRequest(message="The correct name is Amor Vish and he complained via email."))

        self.assertEqual(result.complaint.customerName, "Amor Vish")
        self.assertEqual(result.complaint.source, "Email")

    def test_product_and_strength_are_separate(self):
        result = extract_demo(IntakeRequest(
            message="Apollo Pharmacy reported discolored Amoxicillin Capsules 500 mg from batch AMX240602."
        ))

        self.assertEqual(result.complaint.productName, "Amoxicillin Capsules")
        self.assertEqual(result.complaint.strength, "500 mg")
        self.assertEqual(result.complaint.batchNumber, "AMX240602")
        self.assertEqual(result.complaint.complaintCategory, "Product Quality Issue")

    def test_relative_dates_use_the_reference_date(self):
        reference = date(2026, 9, 10)

        self.assertEqual(resolve_date_expression("after 10 days", reference), "20/09/2026")
        self.assertEqual(resolve_date_expression("yesterday", reference), "09/09/2026")
        self.assertEqual(resolve_date_expression("tomorrow", reference), "11/09/2026")
        self.assertEqual(resolve_date_expression("next Tuesday", reference), "15/09/2026")
        self.assertEqual(
            extract_relative_date_patch("The expedition date is after 10 days.")["expiryDate"],
            resolve_date_expression("after 10 days"),
        )

    def test_relative_manufacturing_date_and_expiry(self):
        result = extract_demo(IntakeRequest(
            message="The manufacturing date is 2024 New Year and the expiry date is after 10 days."
        ))

        self.assertEqual(result.complaint.manufacturingDate, "01/01/2024")
        self.assertEqual(result.complaint.expiryDate, resolve_date_expression("after 10 days"))

    def test_sparse_input_gets_low_information_assessment(self):
        result = extract_demo(IntakeRequest(message="hello"))

        self.assertEqual(result.riskAssessment.severity, "Minor")
        self.assertIn("additional complaint details", result.riskAssessment.suggestedNextAction)

    def test_correction_updates_only_the_requested_expiry(self):
        existing = ComplaintData(
            customerName="Aditya Bhadra",
            productName="Amoxicillin Capsules",
            expiryDate="25/09/2026",
        )
        result = extract_demo(IntakeRequest(
            message="Change the expiration date to today's date",
            existingComplaint=existing,
        ))

        self.assertEqual(result.complaint.expiryDate, format_local_today())
        self.assertEqual(result.complaint.customerName, "Aditya Bhadra")


if __name__ == "__main__":
    unittest.main()
