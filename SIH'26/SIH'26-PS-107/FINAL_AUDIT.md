# BIS Assist - Final Project Audit & SIH Evaluation (PS 26107)

## 1. Problem Addressed
**Problem Statement 26107:** AI-powered Intelligent Assistant for Indian Standards and BIS Services.
MSMEs and manufacturers struggle to navigate dense, highly technical BIS PDFs to find the correct standards, mandatory testing, and certification schemes. BIS Assist resolves this by converting static PDF knowledge into a navigable, relational, evidence-grounded decision-support platform.

## 2. Final Feature List
- **Find My Standard (Parametric Search):** A structured UI where users input product details and the system infers missing parameters to locate candidate standards.
- **Decision Trace:** Transparently explains *why* a standard was selected (matching material, use, capacity) rather than providing a black-box AI recommendation.
- **Evidence Rail:** A dual-pane chat interface where every generated answer is anchored to a persistently visible clause, page, and standard document excerpt.
- **Visual Compliance Pathway:** Dynamically generates the node-based compliance journey (Product → Standard → Testing → Laboratory).
- **Multilingual Support:** Queries can be made in Hindi. The system translates, performs English semantic retrieval, and answers in Hindi while preserving the exact English source citations.
- **Graceful Uncertainty:** The system actively refuses to answer questions lacking evidence ("I could not verify this from the available BIS sources") instead of hallucinating.

## 3. Architecture
- **Frontend:** Next.js (Pages Router) + Tailwind CSS. Designed as a strict "Technical Research Workstation" (no generic AI chat bubbles, no gradients).
- **Backend:** FastAPI (Python) + SQLAlchemy (AsyncORM).
- **Database:** PostgreSQL (structured graph relations + semantic chunks).

## 4. RAG Pipeline
1. **Query Normalization:** `langdetect` intercepts Hindi queries and translates them for internal processing.
2. **Entity Extraction:** An LLM structurally parses the query into a discrete JSON `EntityState` (Product, Material, Intended Use) to build persistent conversational memory without context degradation.
3. **Hybrid Retrieval:** Vector similarity (via `sentence-transformers`) combined with keyword filtering against the `document_chunks` table.
4. **Constrained Generation:** LLM generates the response with strict refusal prompts if chunks are empty.

## 5. Data Architecture
Data is separated into two layers:
- **Relational Graph:** Deterministic relationships between `Laboratory` ↔ `Test` ↔ `Requirement` ↔ `Standard`.
- **Semantic Corpus:** `DocumentChunks` representing clauses from BIS publications.

## 6. Decision Trace
Implemented in the "Find My Standard" module. It exposes:
- **User Input** (What was explicitly stated)
- **System Understanding** (What was inferred)
- **Standard Match** (The exact IS number)
- **Why It Matched** (Matching attributes)
- **Evidence** (The retrieved PDF clause)

## 7. Evidence Architecture
Citations are treated as first-class citizens. The UI will not render a citation link unless a valid ID maps to a retrieved chunk. The UI displays the `Confidence` level strictly as "Supported by source", "Potentially Relevant", or "Needs Confirmation." Numerical AI percentages are banned.

## 8. Multilingual Architecture
Language switching is handled at the API boundaries. The frontend sends `language="hi"`. The backend translates the query to English, retrieves English chunks, generates an English answer grounded in the chunks, and then translates *only the final answer* back to Hindi, ensuring that no semantic drift occurs in the retrieval stage.

## 9. Golden Demo Flow
1. **Find My Standard**: User inputs "Stainless steel water bottle for household drinking water."
2. **Decision Trace**: UI shows it mapped "Household" to "Domestic" and recommends IS 17526:2021.
3. **Ask BIS**: User asks "Are there testing labs for this?"
4. **Evidence Rail**: The UI populates the rail with the exact retrieved clause and verified laboratory details.
5. **Certification Navigator**: User generates the AI-generated informational preparation summary.

## 10. Verified vs Demo Data
**IMPORTANT DEMO NOTICE:** To ensure the system runs independently for the SIH evaluation, the database contains placeholder mock chunks representing BIS standards. The *relational logic* and *RAG extraction pipeline* are real and production-ready, but the *underlying text* is clearly designated as demo data to avoid accidental regulatory misdirection.

## 11. Known Limitations
- Vector retrieval currently runs in-memory. For national-scale deployment, PostgreSQL must be compiled with the `pgvector` extension.
- The UI language dropdown is functional on the backend via hardcoded parameters but requires full React Context integration for dynamic global switching.

## 12. Deployment Instructions
1. `backend/`: `pip install -r requirements.txt`
2. Configure `.env` with `DATABASE_URL` and `OPENAI_API_KEY`.
3. Start FastAPI: `uvicorn app.main:app --reload`
4. `frontend/`: `npm install`
5. Start Next.js: `npm run dev`

## 13. SIH Innovation Points
- **Zero-Hallucination Design Pattern**: The LLM is structurally blocked from fabricating testing laboratories because laboratory recommendations are served via SQL graph traversal, not text generation.
- **Parametric State Machine**: Unlike a stateless chatbot, BIS Assist remembers that a product is "stainless steel" across multiple queries, asking only for missing micro-attributes (e.g. "Is it double-walled?").

---

### WHAT WE SHOULD SAY TO THE JUDGES
1. **"This is not a chatbot; it is a deterministic decision-support system."** We separated the AI language capabilities from the factual database. The AI understands the user, but the SQL graph determines the compliance rules.
2. **"We built a Zero-Hallucination Evidence Rail."** Every claim made by the assistant is permanently tethered to an exact clause and page number visible on the screen. If the evidence isn't in the database, the system is programmed to say it doesn't know.
3. **"We use a Parametric Decision Trace."** Instead of just giving an answer, we show the user *why* a standard was selected based on Material, Intended Use, and Product Category.
4. **"Our Multilingual approach preserves technical accuracy."** By translating the query *before* retrieval, we search the English regulatory corpus accurately, then translate the answer back to Hindi while keeping the English citations intact.
5. **"We designed for MSMEs, not AI enthusiasts."** The UI is intentionally stripped of generic AI branding. It looks and functions like a serious government regulatory workstation.
