# BIS Assist - Demo Guide (SIH 2026)

Welcome to the **BIS Assist** evaluation build. This system demonstrates an evidence-grounded decision-support assistant for Indian Standards and BIS services, utilizing Retrieval-Augmented Generation (RAG) and structured graph relationships.

## 🚀 How to Run the Project

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- PostgreSQL
- OpenAI API Key (optional but recommended for LLM translation/generation)

### Backend Setup
1. Open terminal and navigate to `backend/`.
2. Create a virtual environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` (or create one) and set:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bis_assist
   OPENAI_API_KEY=your_key_here
   ```
5. Run migrations to setup PostgreSQL tables: `alembic upgrade head`.
6. (Optional) Run the database seed script to populate demo data (if provided).
7. Start the FastAPI server: `uvicorn app.main:app --reload`.

### Frontend Setup
1. Open a new terminal and navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Start the Next.js app: `npm run dev`.
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Expected Workflows & Sample Queries

### 1. Ask BIS (RAG Engine)
- **Standard Identification**: "Which standard applies to stainless steel water bottles?"
- **Testing Requirements**: "What tests are required for LED luminaires?"
- **Hallucination Resistance (Test This!)**: "What is the standard for time machines?"
  - *Expected:* The system will strictly refuse and reply: `"I could not verify this from the available BIS sources."`
- **Multilingual Support**: Switch the UI to Hindi and ask a question in Hindi. The response will be in Hindi while citing the original English BIS standard.

### 2. Find My Standard (Structured Assessment)
- Navigate to **Find My Standard**.
- Step through the parameters (Product, Intended Use, Material).
- The system uses structured extraction to map your inputs to candidate standards securely, providing a visual Evidence Rail for the match.

### 3. Certification Navigator
- Enter a product type (e.g., "Steel Pipes").
- The system generates a linear sequence of mandatory steps (Eligibility → Testing → Application), marking the evidence state as **VERIFIED** or **INFERRED**.

### 4. Standards Explorer & Evidence Chain
- Search for a standard (e.g., "IS 1234").
- When viewing a response in Ask BIS, click **View Evidence**. This opens the Evidence Explorer component showing the exact visual chain: `Question → Retrieved Source → Clause Excerpt → Answer Fragment`.

---

## 📊 Data Disclosure: Real vs. Demo

For the purpose of this demonstration:
- **Real/Verified Data Structures**: The schemas, the strict verification states (`VERIFIED`, `NOT_VERIFIED`), and the RAG architecture are production-ready.
- **Demo Data**: The actual chunks of text (e.g., "IS 1234 applies to stainless steel bottles") pre-loaded into the database during testing are mock placeholders meant to simulate BIS publications. They are clearly labeled in the database as demo sources.
- **Do NOT** use the answers provided by this demo instance for actual compliance decisions. 

## ⚠️ Known Limitations
- **Full Text Search**: Currently uses basic `ILIKE` and in-memory vector cosine similarity for the demo. Production deployment will require `pgvector` enabled on the PostgreSQL instance.
- **LLM Rate Limits**: If using a free-tier OpenAI key, rapid queries might trigger rate limiting, resulting in a graceful fallback message (`"System temporarily unavailable: Could not generate a verified answer."`).

## 👥 Team

- Gurkirat Singh
- Heer Chawla