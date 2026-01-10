"""FastAPI application for texting with Claude via Twilio SMS."""

import logging
import os
from collections import defaultdict

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phone AI - Text with Claude")

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# In-memory conversation storage keyed by phone number
# In production, use a proper database
conversations: dict[str, list[dict]] = defaultdict(list)

# System prompt for Claude
SYSTEM_PROMPT = """You are a helpful AI assistant responding via SMS text messages.
Keep your responses concise and suitable for text messaging - aim for under 160 characters when possible,
but you can go longer if necessary to properly answer the question. Be friendly and conversational."""


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "phone-ai"}


@app.post("/sms")
async def handle_sms(
    Body: str = Form(...),
    From: str = Form(...),
):
    """
    Webhook endpoint for incoming Twilio SMS messages.

    Twilio sends POST requests with form data including:
    - Body: The text message content
    - From: The sender's phone number
    """
    incoming_message = Body.strip()
    sender = From
    logger.info(f"Received SMS from {sender}: {incoming_message}")

    # Check allowlist
    allowed = os.getenv("ALLOWED_PHONE_NUMBER")
    if allowed and sender != allowed:
        logger.warning(f"Rejected SMS from {sender} - not in allowlist (allowed: {allowed})")
        return Response(status_code=204)  # Silent ignore

    # Special command to clear conversation history
    if incoming_message.lower() in ["reset", "clear", "new chat"]:
        conversations[sender] = []
        response = MessagingResponse()
        response.message("Conversation cleared! Send me a message to start fresh.")
        return Response(content=str(response), media_type="application/xml")

    # Add user message to conversation history
    conversations[sender].append({"role": "user", "content": incoming_message})

    # Get response from Claude
    try:
        logger.info(f"Calling Claude API with {len(conversations[sender])} messages")
        claude_response = anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=conversations[sender],
        )
        logger.info(f"Claude response: {claude_response}")

        assistant_message = claude_response.content[0].text
        logger.info(f"Assistant message: {assistant_message}")

        # Add assistant response to conversation history
        conversations[sender].append({"role": "assistant", "content": assistant_message})

        # Keep conversation history manageable (last 20 messages)
        if len(conversations[sender]) > 20:
            conversations[sender] = conversations[sender][-20:]

    except Exception as e:
        logger.exception(f"Error calling Claude API: {e}")
        assistant_message = f"Sorry, I encountered an error: {str(e)[:100]}"

    # Create TwiML response
    twiml_response = MessagingResponse()
    twiml_response.message(assistant_message)
    twiml_xml = str(twiml_response)
    logger.info(f"TwiML response: {twiml_xml}")

    return Response(content=twiml_xml, media_type="application/xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
