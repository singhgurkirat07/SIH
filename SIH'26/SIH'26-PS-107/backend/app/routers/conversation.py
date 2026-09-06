# backend/app/routers/conversation.py
"""Router for conversational API (Phase 10)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..schemas.conversation import ConversationalRequest, ConversationalResponse, Message
from ..services.conversation import get_or_create_context, update_context
from ..services.language import translate_text, detect_language
from ..services.retrieval import hybrid_search
from ..services.llm import generate_answer

try:
    from ..database import get_db
except ImportError:
    async def get_db():
        yield None

router = APIRouter(prefix="/api/chat", tags=["Conversational"])
logger = logging.getLogger(__name__)

@router.post("/message", response_model=ConversationalResponse)
async def chat_message_api(
    request: ConversationalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Handle multi-turn conversational message."""
    context = get_or_create_context(request.conversation_id)
    
    # 1. Add to history
    context.history.append(Message(role="user", content=request.message))
    
    # 2. Translate if needed for internal processing (reusing Phase 7 concepts)
    english_query = translate_text(request.message, "en")
    
    # 3. Update structured state and determine if clarification is needed
    entities, needs_clarification, clar_question = update_context(context, english_query)
    
    # 4. If clarification needed, ask it in user's language
    if needs_clarification and clar_question:
        localized_question = translate_text(clar_question, request.language)
        context.history.append(Message(role="assistant", content=localized_question))
        return ConversationalResponse(
            answer=localized_question,
            entities=entities,
            clarification_requested=True,
            citations=[]
        )
        
    # 5. Build search string from structured entities
    search_terms = []
    if entities.product: search_terms.append(entities.product)
    if entities.material: search_terms.append(entities.material)
    if entities.use: search_terms.append(entities.use)
    if entities.capacity: search_terms.append(entities.capacity)
    
    search_query = " ".join(search_terms) if search_terms else english_query
    
    # 6. Retrieve evidence
    chunks = await hybrid_search(db, search_query, top_k=5)
    evidence_dicts = []
    for chunk, score in chunks:
        evidence_dicts.append({
            "source_id": chunk.document.source_id if chunk.document else 0,
            "document_title": chunk.document.title if chunk.document else "Unknown",
            "excerpt": chunk.text,
            "relevance_score": score
        })
        
    # 7. Generate answer
    # Provide the structured state to the LLM to ground the answer
    context_str = "\n".join(f"{k}: {v}" for k, v in entities.dict().items() if v)
    prompt_query = f"Context:\n{context_str}\n\nQuestion: {english_query}"
    
    english_answer = generate_answer(prompt_query, evidence_dicts)
    localized_answer = translate_text(english_answer, request.language)
    
    context.history.append(Message(role="assistant", content=localized_answer))
    
    return ConversationalResponse(
        answer=localized_answer,
        entities=entities,
        clarification_requested=False,
        citations=evidence_dicts
    )
