# CCMS Video Submission Guide

This guide prepares two separate private videos for the AIVOA.AI Round 1 AI Product Engineer assignment:

1. Product Demonstration Video
2. Code Explanation Video

Target duration: 5-10 minutes for each video.

Audience: interviewers and technical judges.

Tone: technical, confident, and interview-oriented.

## 1. Requirements and scope

The assignment requires React with Redux, FastAPI, LangGraph, Groq, MySQL or PostgreSQL, and Google Inter. It asks for two videos: one demonstrating the implemented AI tools and frontend features, and one explaining the complete request lifecycle from frontend input through the API, backend, AI/LangGraph workflow, and final UI output.

The assignment also states that production-grade OCR or document parsing is not required. The demonstration should therefore describe the document feature accurately as text extraction from supported PDF, DOCX, TXT, and EML inputs. Do not claim handwriting OCR, scanned-image OCR, or production document intelligence.

The project currently uses:

- Project name: CCMS - AI-Powered Customer Complaint Management System.
- Frontend: React, Vite, Redux Toolkit, and Lucide icons.
- Backend: Python and FastAPI.
- AI orchestration: LangGraph.
- LLM integration: Groq using the configured `openai/gpt-oss-20b` model.
- Database: PostgreSQL running locally through Docker.
- Date handling: application-local `Asia/Kolkata` timezone.
- Persistence: complaint records, risk assessment, extraction metadata, and duplicate fingerprints.
- Demo fallback: deterministic local extraction when the Groq key or service is unavailable.

The original assignment references `gemma2-9b-it` and optionally `llama-3.3-70b-versatile`. The current implementation uses `openai/gpt-oss-20b` because the originally planned models were not reliably available in the target environment. State this clearly if discussing model selection.

## 2. Recording preparation

### Environment checklist

Before recording:

1. Start Docker Desktop.
2. Open a terminal in the repository root.
3. Run `docker compose up -d postgres`.
4. Start the backend with the project Python environment:

   ```powershell
   backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
   ```

5. Start the frontend in a second terminal:

   ```powershell
   npm run dev
   ```

6. Open the local Vite URL in a clean browser window.
7. Confirm the backend health indicator is available and the Co-Pilot is using live AI. If the UI shows Demo mode, do not record the live-AI claims until the backend environment is corrected.
8. Keep the Groq API key, `.env` file, terminal secrets, and database credentials off-screen.

### Database preparation

Use a clean PostgreSQL database with one or two records. The first video should create at least one record during the recording so the save flow is visible. If records already exist, open Saved Complaints before recording and remove only disposable demo records.

Do not reset PostgreSQL IDs for presentation purposes. SQL primary keys are intentionally monotonic and may show gaps after deletion.

### Recommended sample inputs

Use the following inputs in this order. They cover the required initial complaint, edit tool, document extraction tool, and post-document correction.

#### Input A: complete text complaint

```text
Apollo Pharmacy complained via email about discolored Amoxicillin Capsules 500 mg. The batch number is AMX240602. It was manufactured on 1 March 2026 and expires on 28 February 2028. Twelve capsules are affected. The complaint date is 18 June 2026. Please log this product quality complaint and assess the initial risk.
```

Expected result:

- Customer Name: Apollo Pharmacy.
- Complaint Source: Email.
- Product Name: Amoxicillin Capsules.
- Strength: 500 mg.
- Batch/Lot Number: AMX240602.
- Manufacturing Date: 01/03/2026.
- Expiry Date: 28/02/2028.
- Quantity: 12 capsules.
- Complaint Category: Product Quality Issue.
- Complaint Date: 18/06/2026.
- Description: an AI-generated professional complaint summary.
- Risk assessment: a populated severity, suggested action, and initial risk assessment.

The exact wording of the AI-generated description and assessment can vary. The important points are field population, preservation of explicit facts, and clear risk reasoning.

#### Input B: text correction

```text
Correction: the batch number is AMX240602B and the affected quantity is 24 capsules. Keep every other field unchanged.
```

Expected result:

- Batch/Lot Number changes to AMX240602B.
- Quantity changes to 24 capsules.
- Customer, product, dates, category, and description remain present.
- The assessment remains populated and can be recalculated by the workflow.

#### Input C: document extraction

Prepare a realistic PDF before recording. Use a file named `Metformin_API_Complaint_Report.pdf` with text similar to:

```text
Customer: Nova Pharma Manufacturing
Complaint source: Quality email
Product: Metformin hydrochloride API
Strength/Grade: IP/BP
Batch/Lot: MFH260712A
Manufacturing date: 12 July 2026
Expiry date: 11 July 2028
Affected quantity: 50 kg in 2 HDPE drums
Complaint date: 15 July 2026
Issue: The API powder was reported to have an unexpected grey appearance and non-uniform particle texture. The material has been quarantined pending investigation.
```

Expected result:

- The PDF is accepted by the upload control.
- The backend extracts the document text.
- The AI maps the document into the complaint fields.
- The risk assessment is generated from the document context.
- The source filename is shown in the Co-Pilot history.

#### Input D: post-document correction

```text
Correction after the PDF extraction: the batch number is CHG260712A and the affected quantity is 50 kg in 2 HDPE drums. Preserve all other extracted details.
```

Expected result:

- Batch/Lot Number changes to CHG260712A.
- Quantity is preserved as 50 kg in 2 HDPE drums.
- All other extracted details remain available.

## 3. Video 1 - Product Demonstration Script

Target length: approximately 7-8 minutes.

### 0:00-0:30 - Introduction

Screen: clean application home screen with the complaint form on the left and AIVOA Co-Pilot on the right.

Action: do not click yet. Keep the initial form visible.

Narration:

> This is CCMS, an AI-powered customer complaint management system for pharmaceutical quality teams. The application accepts a complaint through natural language or a supported document, extracts structured complaint information, generates an initial risk assessment, lets the user correct the result conversationally, and saves the reviewed record to PostgreSQL. The goal is to reduce manual transcription while keeping the complaint information visible for human review.

Recording notes:

- Keep the full two-column layout visible.
- Do not show terminal windows or environment variables.
- Point out that the form is intentionally empty at the start.

### 0:30-1:00 - Explain the workflow and the safety boundary

Screen: slowly move the cursor over the form sections and the Co-Pilot composer.

Action: point to the empty fields, upload area, and message composer.

Narration:

> The left side is the Complaint Log. It contains customer, product, batch, date, quantity, category, and description fields. The right side is the AIVOA Co-Pilot. I do not fill the complaint form manually for this demonstration. I provide the complaint to the Co-Pilot, and the extraction response populates the form. The result is still reviewed by a human before it is saved.

> This implementation supports text and text-based document extraction. Production-grade OCR for scanned handwriting or image-only documents is outside the assignment scope and is not being claimed here.

### 1:00-2:15 - Demonstrate the Log Complaint Tool

Screen: Co-Pilot message composer.

Action: paste Input A and click Send.

Narration before sending:

> I will start with a complete customer complaint containing identity, source, product, strength, batch, manufacturing date, expiry date, quantity, complaint date, and a product-quality defect.

Action: paste the complete text complaint and send it.

Expected output to point at:

- The user message appears in the chat.
- The extraction progress card appears.
- The form fields populate.
- The AI risk assessment changes from empty to populated.
- The status changes to Ready to Review.

Narration after the response:

> The AI has extracted the complaint into the structured form. Notice that the customer and source are separate fields, the product and strength are separate fields, and the batch and dates are mapped independently. The complaint category and description were generated for quality review. The Co-Pilot also generated an initial severity, a next action, and a risk summary.

> The green field highlights are temporary review cues. They show which fields were populated by extraction; they are not a replacement for human verification.

Camera instructions:

- Pause for two seconds after extraction completes.
- Scroll the left form slowly enough to show all populated sections.
- Zoom in briefly on the risk assessment section.
- Do not read every generated sentence aloud; explain the important fields.

### 2:15-3:00 - Demonstrate risk assessment and review

Screen: AI Copilot risk assessment section.

Action: point to Severity, Suggested Next Action, and Initial Risk Assessment.

Narration:

> The risk assessment is intentionally presented as a recommendation for review, not as an autonomous final disposition. The severity summarizes the reported quality concern, the suggested action gives the reviewer a practical next step, and the initial risk assessment explains the reasoning in business language. The user can review the full complaint before saving it to the QMS ledger.

If the severity badge is visible, say:

> The severity badge makes the risk level scannable while the detailed text remains available for context. Low, medium, high, and critical states use different semantic colors in both Light and Dark themes.

### 3:00-3:45 - Demonstrate the Edit Complaint Tool

Screen: Co-Pilot composer with the populated form still visible.

Action: paste Input B and click Send.

Narration before sending:

> Now I will correct only the batch number and affected quantity using natural language. This tests whether the system can update selected fields without losing the rest of the complaint.

Expected output:

- Batch changes from AMX240602 to AMX240602B.
- Quantity changes from 12 capsules to 24 capsules.
- Other fields remain populated.
- The changed fields are highlighted.

Narration after the response:

> The correction was applied to the requested fields. The existing complaint was sent with the new message, so the extraction workflow can preserve known values while applying explicit corrections. This is important because complaint intake is iterative: a customer or QA reviewer may correct a batch number after the first report.

### 3:45-5:15 - Demonstrate the Document Extraction Tool

Screen: file upload control in the Co-Pilot.

Action: click the upload control and choose `Metformin_API_Complaint_Report.pdf`.

Narration before upload:

> Next I will demonstrate the document extraction tool. This PDF contains a different API complaint, including a product grade, batch, dates, quantity, defect description, and quarantine context.

Expected output:

- The uploaded filename appears in the chat history.
- The form changes to the Metformin complaint details.
- The assessment is regenerated for the new complaint.
- The extraction progress moves from processing to completed.

Narration after extraction:

> The document parser extracts text from the PDF and sends the text through the same complaint intake workflow. The result is not a separate manual form process; it reaches the same structured complaint schema and risk assessment path as typed text.

Camera instructions:

- Show the filename, not the file contents outside the application.
- Scroll to show product, grade, batch, quantity, and description.
- Pause on the assessment to show the workflow produced both structured data and reasoning.

### 5:15-5:55 - Demonstrate a post-document correction

Screen: Co-Pilot composer with the PDF result populated.

Action: paste Input D and click Send.

Narration:

> Document extraction is also editable through the same conversational interface. I will correct the batch and confirm the quantity while preserving the other PDF-derived fields.

Expected output:

- Batch changes to CHG260712A.
- Quantity remains 50 kg in 2 HDPE drums.
- Product, grade, dates, category, and description remain available.

### 5:55-6:50 - Save and review the QMS record

Screen: Save Complaint button, then Saved Complaints viewer.

Action: click Save Complaint. Wait for the status to show Saved to Local QMS. Click Saved Complaints.

Narration:

> After reviewing the extracted and corrected values, I can save the complaint. The frontend sends the structured complaint, risk assessment, source text, extraction mode, changed fields, and missing fields to the FastAPI save endpoint. The backend stores the record in PostgreSQL.

> The Saved Complaints viewer reads the saved records back from the API. It provides a compact review list, lets me reopen a saved complaint, and includes a delete action for disposable local records.

Expected output:

- Save status confirms the record.
- Saved Complaints shows the record ID, customer, product, date, severity, and mode.
- Opening a record restores the form and assessment.

### 6:50-7:20 - Demonstrate duplicate protection

Screen: Saved Complaints viewer or form.

Action: return to the same populated record and click Save Complaint again, or repeat the same save payload.

Narration:

> If the same complaint is saved again, the backend does not create a second record. Duplicate detection uses the stable complaint fields and intentionally excludes the AI-generated description and assessment wording, because those can vary slightly between runs. The database ID remains a stable audit identifier and is not reused after deletion.

Expected output: status changes to Already Saved.

### 7:20-7:50 - Show theme and responsive experience

Screen: form header and the theme toggle.

Action: click the theme toggle. Show the dark theme, then collapse the Co-Pilot. If time allows, show the mobile drawer at a narrow viewport.

Narration:

> The application also supports a persisted Light and Dark theme. The semantic status tokens keep pending, success, error, review, and risk states distinguishable in both modes. The Co-Pilot can be collapsed on desktop, and on smaller screens it behaves as an overlay drawer while the complaint form remains full width.

### 7:50-8:00 - Conclusion

Screen: return to the populated complaint and risk assessment, preferably in Light Theme for maximum readability.

Narration:

> CCMS turns unstructured complaint text or a supported document into a reviewable quality record, adds an explainable initial risk assessment, supports natural-language corrections, and persists the reviewed result in PostgreSQL. The design keeps the human reviewer in control while reducing repetitive complaint data entry.

## 4. Product demonstration recording guide

### Recommended recording order

1. Start with the empty form and Co-Pilot.
2. Run the complete text complaint.
3. Show the populated form and risk assessment.
4. Run the batch and quantity correction.
5. Upload the realistic PDF.
6. Run the post-document correction.
7. Save the record.
8. Open Saved Complaints and reopen the record.
9. Demonstrate duplicate protection.
10. Show the theme toggle and Co-Pilot collapse briefly.

### Product-demo emphasis

- The form is populated by AI rather than manually.
- The customer name and complaint source are separate concepts.
- Product name and strength are separate fields.
- Relative or corrected values are handled conversationally.
- Risk assessment is generated but remains a human-review recommendation.
- Document extraction and typed extraction share the same workflow.
- Persistence and duplicate protection make the result useful beyond a visual demo.

### Product-demo mistakes to avoid

- Do not show an API key, `.env`, or database password.
- Do not claim production OCR.
- Do not manually type into the left form before demonstrating AI intake.
- Do not delete a real record during the recording.
- Do not wait silently while an extraction runs; narrate what the workflow is doing.
- Do not use a complaint with missing details if the goal is to demonstrate complete extraction.
- Do not present an AI severity as a final regulatory decision.

## 5. Video 2 - Code Explanation Script

Target length: approximately 8-10 minutes.

The code video should be recorded after the product demo and should use the same sample flow. Keep the editor or file browser at a readable zoom and reveal only the relevant functions. Do not scroll aimlessly through every line.

### 0:00-0:35 - Project and architecture overview

Screen: repository root showing `src`, `backend`, `docker-compose.yml`, `package.json`, and `README.md`.

Narration:

> This is the CCMS repository. The frontend is a React and Vite application with Redux Toolkit for complaint state. The backend is a FastAPI service. The AI workflow is implemented with LangGraph and Groq. PostgreSQL runs locally through Docker. The important architectural boundary is that the frontend owns presentation and user interaction, the API layer owns HTTP communication, the backend services own extraction and persistence, and the database owns saved complaint records.

Point to:

- `src/`
- `backend/app/`
- `docker-compose.yml`
- `backend/requirements.txt`
- `package.json`

### 0:35-1:10 - Frontend entry point and Redux state

Screen: open `src/main.jsx`, then `src/store.js`.

Narration:

> `src/main.jsx` creates the React root, wraps the application with the Redux Provider, and loads the global stylesheet. `src/store.js` defines the initial complaint shape and the two main reducers: `updateComplaint`, which merges extracted or edited fields, and `resetComplaint`, which returns the form to its empty state.

Highlight:

- `createRoot(...)`
- `<Provider store={store}>`
- `initialComplaint`
- `updateComplaint`
- `resetComplaint`

Explain:

> Keeping the complaint object in Redux gives the form and other frontend components a single source of truth. The AI response can update the same state that the form renders.

### 1:10-2:10 - Main page and user actions

Screen: open `src/App.jsx`.

Narration:

> `App.jsx` coordinates the single-page user journey. It reads the complaint from Redux, owns the conversational state, tracks extraction progress, stores the risk assessment, persists the theme and Co-Pilot visibility, and connects UI actions to the API service.

Show these functions in order:

1. `submitMessage`
2. `handleFileUpload`
3. `handleSaveComplaint`
4. `openSavedViewer`
5. `openSavedRecord`
6. `deleteSavedRecord`
7. `startNewChat`

Narration:

> Text input enters through `submitMessage`. File input enters through `handleFileUpload`. Both paths update the same complaint state and risk-assessment state after the API returns. Save, list, reopen, and delete are separate record actions. The fallback path is intentionally local and deterministic, so the application remains usable when the model key or network is unavailable.

### 2:10-2:55 - Reusable complaint form components

Screen: open the following files:

- `src/components/complaint/ComplaintForm.jsx`
- `src/components/complaint/ComplaintSection.jsx`
- `src/components/complaint/ComplaintField.jsx`
- `src/features/complaint/complaintConfig.js`

Narration:

> The complaint form is data-driven. `complaintConfig.js` defines sections and field metadata. `ComplaintForm` maps sections, `ComplaintSection` maps fields, and `ComplaintField` renders the correct control based on the field type. This means adding a field usually requires configuration rather than a new hard-coded form block.

> `ComplaintField` also owns date-specific behavior: display-format validation, conversion to the native date picker, and the temporary error message. The component exposes a small API: a field definition, current value, change callback, and extraction-state flags.

### 2:55-3:25 - Risk assessment and saved viewer

Screen: open `src/components/complaint/AiAssessment.jsx` and `src/components/complaint/SavedComplaintsViewer.jsx`.

Narration:

> `AiAssessment` is presentation-only. It receives the assessment object and maps the severity to a semantic visual class. It does not call the model or decide the risk. `SavedComplaintsViewer` is also presentation-focused: it receives records and callbacks for opening or deleting a record.

> This separation keeps the main page responsible for workflow orchestration while the child components remain reusable and easy to test.

### 3:25-4:00 - Frontend API layer

Screen: open `src/services/complaintApi.js`.

Narration:

> The frontend does not build HTTP requests inside each component. `complaintApi.js` centralizes the API base URL and exposes small functions for health, text intake, file intake, save, list, and delete operations.

Highlight:

- `intakeComplaint` uses `POST /api/complaints/intake`.
- `intakeComplaintFile` uses `POST /api/complaints/intake-file` with `FormData`.
- `saveComplaint` uses `POST /api/complaints`.
- `listComplaints` uses `GET /api/complaints`.
- `deleteComplaint` uses `DELETE /api/complaints/{id}`.

### 4:00-4:35 - FastAPI route layer

Screen: open `backend/app/main.py`.

Narration:

> FastAPI receives the frontend requests and validates payloads through Pydantic schemas. The intake route accepts text and an optional existing complaint. The file route reads the uploaded file, extracts document text, and converts the result into the same intake request shape. This is an important design choice: text and document inputs converge on one complaint extraction interface.

Highlight:

- `@app.post("/api/complaints/intake")`
- `@app.post("/api/complaints/intake-file")`
- `extract_document_text(...)`
- `extract_complaint(request)`

### 4:35-5:20 - Service selection and fallback behavior

Screen: open `backend/app/services/intake_service.py`.

Narration:

> `extract_complaint` is the provider boundary. If no Groq key is configured, it uses the deterministic demo extractor. If a key is configured, it uses the LangGraph and Groq workflow. If the live workflow raises an exception, the service logs the failure and falls back to deterministic extraction. This keeps local development and demonstrations resilient without hiding the distinction between live and demo mode.

### 5:20-6:45 - LangGraph workflow

Screen: open `backend/app/services/langgraph_extractor.py`.

Narration:

> The live AI path uses a small sequential LangGraph workflow with three nodes. The state contains the intake request, the first model pass, the second model pass, and the final response.

Show the nodes in this order:

1. `_extract_pass_one`
2. `_extract_pass_two`
3. `_finalize_node`

Narration:

> Pass one extracts every explicit fact, normalizes dates, generates a category and risk assessment, and preserves known values. Pass two re-analyzes specifically for missing fields and leaves low-confidence values empty rather than inventing them. This two-pass design improves completeness while preserving a conservative extraction policy.

> `_get_structured_llm` creates the `ChatGroq` client with the configured model and temperature zero. The workflow uses JSON mode mapped into the `ExtractedComplaint` Pydantic model. This is used because the selected model reliably returns structured JSON but may not emit a tool call.

> `_finalize_node` merges the existing complaint, both model outputs, and deterministic safeguards. It applies explicit correction parsing, relative-date resolution, identity/source separation, complaint-date defaults, required-field tracking, and the final `RiskAssessment` object.

Show the graph construction:

> `build_extraction_graph` connects START to pass one, pass one to pass two, pass two to finalize, and finalize to END. `extract_with_langgraph` invokes that graph and returns the typed response to FastAPI.

### 6:45-7:30 - Deterministic safeguards and document parsing

Screen: open:

- `backend/app/services/demo_extractor.py`
- `backend/app/services/document_parser.py`
- `backend/app/services/date_resolution.py`
- `backend/app/services/extraction_examples.py`

Narration:

> The deterministic extractor is more than a hard-coded demo. It handles common identity, product, strength, batch, date, category, and correction patterns and provides a low-information risk safeguard. The document parser uses `pypdf` for PDF text, `python-docx` for DOCX text, and direct decoding for text-based formats.

> `date_resolution.py` makes relative expressions reproducible using the application timezone. It resolves today, yesterday, tomorrow, after N days, next weekdays, and New Year expressions. Few-shot examples are stored in `extraction_examples.py` and included in the live prompts so the model sees the desired field-separation behavior.

### 7:30-8:20 - Database and duplicate protection

Screen: open:

- `backend/app/schemas.py`
- `backend/app/models.py`
- `backend/app/database.py`
- relevant save code in `backend/app/main.py`

Narration:

> The Pydantic schemas define the API contract for complaint data, risk assessment, intake, and saved records. The SQLAlchemy model stores the complaint and assessment JSON along with original text, source file, extraction mode, changed fields, missing fields, a fingerprint, and creation time.

> Before inserting, the save route creates a fingerprint from stable complaint fields and excludes the AI-generated description. It then checks PostgreSQL for an existing fingerprint. This prevents a second record when only AI wording changes. The delete route removes a specific record by ID, while the list route returns records for the Saved Complaints viewer.

### 8:20-9:00 - End-to-end response and UI rendering

Screen: split view between the API code and the running application, then return to the form.

Narration:

> The response returns the typed complaint, risk assessment, changed fields, missing fields, source filename, and extraction mode. `App.jsx` dispatches the complaint into Redux, stores the assessment in local component state, highlights changed fields, updates the progress state, and renders the result through `ComplaintForm` and `AiAssessment`.

> The same response shape is used whether the user typed a complaint, uploaded a PDF, used the live Groq workflow, or used the deterministic fallback. That keeps the UI stable while allowing the extraction provider to evolve.

### 9:00-9:40 - Architecture trade-offs and conclusion

Screen: return to the repository tree and then the running application.

Narration:

> The architecture is intentionally small for a single-page assignment. React and Redux keep the user interface predictable, FastAPI provides a clear API boundary, LangGraph makes the extraction sequence explicit, and PostgreSQL provides durable records. The main future scaling opportunity would be to extract the page orchestration into dedicated hooks and Co-Pilot components as more pages or workflows are added. For this assignment, the current implementation keeps the full user journey visible and explainable.

> The complete flow is: user input in the React Co-Pilot, a frontend API request, FastAPI validation, document parsing when needed, provider selection, LangGraph extraction passes, deterministic finalization, PostgreSQL persistence when saved, and Redux-driven rendering back into the complaint form and risk assessment.

## 6. Code explanation recording guide

### Exact screen order

1. Repository root.
2. `src/main.jsx`.
3. `src/store.js`.
4. `src/App.jsx`.
5. Complaint form components and configuration.
6. `AiAssessment.jsx` and `SavedComplaintsViewer.jsx`.
7. `src/services/complaintApi.js`.
8. `backend/app/main.py` routes.
9. `intake_service.py` provider boundary.
10. `langgraph_extractor.py` graph and nodes.
11. `demo_extractor.py`, `document_parser.py`, `date_resolution.py`, and examples.
12. `schemas.py`, `models.py`, and `database.py`.
13. Running UI showing the final response.

### Code-video recording rules

- Use a readable font size and highlight only the relevant function.
- Keep the terminal hidden except when showing a safe command such as starting the server.
- Never reveal `.env`, API keys, passwords, or raw database connection secrets.
- Do not claim that the model fine-tunes itself. The project uses prompt examples, structured output, deterministic safeguards, and a fallback extractor.
- Explain that the AI response is validated and post-processed before it reaches the UI.
- Always connect the code explanation back to the visible product result.

## 7. Interview and judge Q&A

### Why did you use LangGraph?

LangGraph makes the extraction workflow explicit as a sequence of stateful nodes. It gives the project a clear place for multiple extraction passes and deterministic finalization, and it can be extended later with review, classification, or CAPA nodes.

### Why are there two extraction passes?

The first pass extracts the main complaint. The second pass focuses on missing fields and high-confidence corrections. This improves completeness without encouraging the model to guess uncertain names, batches, quantities, or dates.

### Why is the finalization logic deterministic?

Dates, identity/source separation, corrections, and required-field tracking are important enough to protect with deterministic logic. The model provides useful semantic extraction and assessment, while deterministic rules enforce predictable application behavior.

### Why is the model `openai/gpt-oss-20b` instead of the model named in the assignment?

The originally planned models were not reliably available in the target access tier and deployment environment. The configuration was changed to `openai/gpt-oss-20b` to keep the integration stable. The provider boundary and structured schema keep the system model-agnostic.

### Is this production OCR?

No. The assignment explicitly says production-grade OCR or document parsing is not required. This implementation extracts text from supported text-based documents and sends that text through the complaint workflow. A future production system could add OCR, malware scanning, file-size enforcement, richer MIME validation, and document provenance controls.

### How does the system handle model failure?

The backend catches live extraction failures and falls back to deterministic local extraction. The response includes a mode so the UI can distinguish live AI from demo behavior.

### How do you prevent duplicate complaints?

The save route hashes stable complaint fields and excludes the AI-generated description and assessment wording. It checks the fingerprint before inserting. A repeated save returns the existing record as already saved.

### Why do deleted record IDs not get reused?

The PostgreSQL ID is a stable primary key and audit identifier. Reusing IDs could make old references ambiguous, so gaps are intentional.

### How does the application handle dates like today or after ten days?

The application resolves relative dates in the `Asia/Kolkata` timezone. The current local date is provided to the live prompt, and deterministic date utilities apply the same reference date to today, yesterday, tomorrow, durations, weekdays, and New Year expressions.

### Why is the AI risk assessment not editable directly?

It is presented as an AI recommendation. The complaint fields remain reviewable, and the workflow supports conversational corrections. Keeping the assessment output visibly AI-generated avoids implying that the model has made a final quality or regulatory decision.

### What would you improve next?

The next production steps would be authentication and authorization, audit history, stronger file validation, OCR for scanned documents, background processing for large files, observability, provider-independent model configuration, and deployment with managed PostgreSQL and secret management.

## 8. Final recording checklist

### Product demonstration

- [ ] Video is between 5 and 10 minutes.
- [ ] Project name is introduced as CCMS.
- [ ] Empty form and Co-Pilot are shown first.
- [ ] Complete text complaint is submitted through the Co-Pilot.
- [ ] All important extracted fields are shown.
- [ ] AI risk assessment is shown and described as a recommendation.
- [ ] Text correction is demonstrated.
- [ ] PDF upload is demonstrated.
- [ ] Post-document correction is demonstrated.
- [ ] Complaint is saved to PostgreSQL.
- [ ] Saved Complaints viewer is opened.
- [ ] Duplicate-save protection is demonstrated or explained.
- [ ] Light/Dark theme and Co-Pilot behavior are shown briefly.
- [ ] No credentials or unfinished feature claims appear on screen.

### Code explanation

- [ ] Video is between 5 and 10 minutes.
- [ ] Frontend, backend, LangGraph, and database layers are all shown.
- [ ] The exact request lifecycle is explained.
- [ ] Text and file intake convergence is explained.
- [ ] Both LangGraph passes and finalization are explained.
- [ ] Fallback behavior is explained.
- [ ] Date resolution and few-shot examples are explained.
- [ ] PostgreSQL save and duplicate fingerprint logic are explained.
- [ ] The final response-to-UI path is shown.
- [ ] No API key or password is visible.
- [ ] The explanation uses the actual current file and function names.

### Submission checklist

- [ ] Product demonstration video is exported separately.
- [ ] Code explanation video is exported separately.
- [ ] Both videos are private or unlisted according to the submission instructions.
- [ ] The GitHub repository URL is ready.
- [ ] Video links are tested in an incognito or separate browser session.
- [ ] The submission form receives the correct video in the correct upload field.
