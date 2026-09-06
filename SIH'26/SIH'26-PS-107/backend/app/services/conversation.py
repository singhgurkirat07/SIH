# backend/app/services/conversation.py
"""Service for conversational intelligence and clarification engine."""
import json
import logging
import os
from typing import Tuple
import openai

from ..schemas.conversation import ConversationContext, EntityState

logger = logging.getLogger(__name__)

# Simple in-memory store for demo. In production, use Redis or Postgres.
CONVERSATION_STORE = {}

def get_or_create_context(conversation_id: str) -> ConversationContext:
    if conversation_id not in CONVERSATION_STORE:
        CONVERSATION_STORE[conversation_id] = ConversationContext(conversation_id=conversation_id)
    return CONVERSATION_STORE[conversation_id]

def update_context(context: ConversationContext, user_message: str) -> Tuple[EntityState, bool, str]:
    """
    Updates the entity state using LLM extraction based on the latest user message.
    Also decides if clarification is needed.
    Returns: (updated_entities, needs_clarification, clarification_question)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No API key. Returning naive extraction.")
        context.entities.product = user_message # Naive fallback
        return context.entities, False, ""

    openai.api_key = api_key
    
    # Prompt LLM to update entities and determine if a clarifying question is needed
    system_prompt = """
    You are managing the conversational state for a BIS Standards Assistant.
    Extract the following entities from the user's message if they are mentioned or corrected:
    product, material, use, capacity, industry, location, technical_attributes (list), selected_standard.
    
    If the user corrects a previous entity (e.g. "No, it's for industrial use"), update the entity accordingly.
    
    Current state:
    {current_state}
    
    If the product is known but you need ONE crucial detail to narrow down the standard (e.g., material, use, or food-contact), ask a single clarifying question. Do not ask more than one question. If the state is sufficient to search, set 'needs_clarification' to false.
    
    Return a JSON object with this exact schema:
    {
        "entities": {
            "product": string|null,
            "material": string|null,
            "use": string|null,
            "capacity": string|null,
            "industry": string|null,
            "location": string|null,
            "technical_attributes": [string],
            "selected_standard": string|null
        },
        "needs_clarification": boolean,
        "clarification_question": string|null
    }
    """
    
    try:
        response = openai.ChatCompletion.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt.replace("{current_state}", context.entities.json())},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        
        # Update state
        new_entities = EntityState(**result.get("entities", {}))
        context.entities = new_entities
        
        needs_clarification = result.get("needs_clarification", False)
        question = result.get("clarification_question", "")
        
        return new_entities, needs_clarification, question
    except Exception as exc:
        logger.error("Failed to update context: %s", exc)
        return context.entities, False, ""
