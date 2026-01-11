# textmaxxing

> Your SMS grindset coach. Claude on speed dial. Touch grass optional.

A FastAPI application that lets you have SMS conversations with Claude using Twilio.

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key from https://console.anthropic.com/

Optionally, set `ALLOWED_PHONE_NUMBER=+1XXXXXXXXXX` to restrict access to a single phone number (E.164 format).

### 3. Run the server

```bash
uv run uvicorn main:app --reload --port 8000
```

### 4. Expose to the internet

Twilio needs a public URL to send webhooks. Use ngrok or similar:

```bash
ngrok http 8000
```

### 5. Configure Twilio

1. Get a phone number from [Twilio Console](https://console.twilio.com/)
2. Go to Phone Numbers → Manage → Active Numbers → Your Number
3. Under "Messaging Configuration":
   - Set webhook URL to: `https://your-ngrok-url.ngrok.io/sms`
   - Set HTTP method to: `POST`

## Usage

Text your Twilio phone number and Claude will respond!

**Special commands:**
- `reset`, `clear`, or `new chat` - Clear conversation history

## Development

```bash
# Run with auto-reload
uv run uvicorn main:app --reload

# Run directly
uv run python main.py
```

## Production Deployment

I recommend deployment via [Railway](https://railway.com?referralCode=amd527).
