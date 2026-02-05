# Vercel Deployment Setup

## Environment Variables Configuration

To enable the AI chat functionality, you need to configure environment variables in your Vercel project.

### Required Environment Variables

1. **ANTHROPIC_API_KEY** (Required)
   - Your Anthropic API key for Claude
   - Get your API key from: https://console.anthropic.com/
   - Example: `sk-ant-api03-...`

2. **AI_MODEL** (Optional)
   - The Claude model to use for responses
   - Default: `claude-sonnet-4-5-20250929`
   - Options:
     - `claude-sonnet-4-5-20250929` (Recommended - Latest Sonnet 4.5)
     - `claude-3-5-sonnet-20241022` (Claude 3.5 Sonnet)
     - `claude-3-haiku-20240307` (Faster, lower cost)

### How to Add Environment Variables in Vercel

#### Option 1: Via Vercel Dashboard

1. Go to your Vercel project dashboard
2. Click on **Settings** tab
3. Click on **Environment Variables** in the left sidebar
4. Add the following variables:

   **Variable Name:** `ANTHROPIC_API_KEY`
   **Value:** Your Anthropic API key (e.g., `sk-ant-api03-...`)
   **Environment:** Production, Preview, Development (select all)

   **Variable Name:** `AI_MODEL` (optional)
   **Value:** `claude-sonnet-4-5-20250929`
   **Environment:** Production, Preview, Development (select all)

5. Click **Save**
6. **Redeploy** your application for changes to take effect

#### Option 2: Via Vercel CLI

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Add environment variables
vercel env add ANTHROPIC_API_KEY
# Paste your API key when prompted
# Select: Production, Preview, Development

vercel env add AI_MODEL
# Enter: claude-sonnet-4-5-20250929
# Select: Production, Preview, Development

# Redeploy
vercel --prod
```

### How It Works

1. **User sends chat message** → Frontend calls `/api/chat`
2. **Vercel serverless function** → Reads `ANTHROPIC_API_KEY` from environment
3. **Server-side API call** → Calls Anthropic API with the key
4. **Response returned** → AI response sent back to frontend

### Benefits of Server-Side API

✅ **Security**: API key never exposed to the client browser
✅ **Control**: Manage API usage centrally on the server
✅ **Flexibility**: Easy to add rate limiting, logging, authentication
✅ **Safety**: No risk of API key being stolen from client-side code

### Demo Mode Fallback

If `ANTHROPIC_API_KEY` is not configured:
- The app automatically falls back to **Demo Mode**
- Users see simulated responses for common NDIS queries
- A warning badge shows "Demo Mode" instead of "AI Active"

### Testing Your Setup

1. Deploy to Vercel with environment variables configured
2. Open the deployed site
3. Go to the **Chat** page
4. Check the status badge:
   - ✅ **AI Active** (green) = API key configured correctly
   - ⚠️ **Demo Mode** (yellow) = API key not configured or invalid

5. Send a test message:
   - If working: You'll get real AI responses
   - If not working: Check the Vercel function logs for errors

### Troubleshooting

**Problem:** Badge shows "Demo Mode" even after adding API key

**Solutions:**
1. Check that you added the variable to all environments (Production, Preview, Development)
2. Make sure you **redeployed** after adding the environment variable
3. Check Vercel Function logs for errors:
   - Go to Vercel Dashboard → Deployments → Select deployment → Functions → `/api/chat`

**Problem:** "Invalid API key" error

**Solutions:**
1. Verify your API key is correct at https://console.anthropic.com/
2. Make sure there are no extra spaces or quotes in the environment variable value
3. Check that your Anthropic account has available credits

**Problem:** Rate limit errors

**Solutions:**
1. Check your Anthropic account usage at https://console.anthropic.com/
2. Consider upgrading your Anthropic plan if needed
3. Implement rate limiting in the `/api/chat.js` function

### Cost Considerations

- **Claude Sonnet 4.5**: Most capable model, higher cost
- **Claude 3.5 Sonnet**: Good balance of capability and cost
- **Claude 3 Haiku**: Fastest and lowest cost

Typical costs (as of 2026):
- Input: ~$3-15 per million tokens (depending on model)
- Output: ~$15-75 per million tokens (depending on model)

For typical NDIS queries:
- Average query: ~500 input + 500 output tokens
- Cost per query: ~$0.01 - $0.05 (depending on model)
- 1000 queries/month: ~$10 - $50

### Next Steps

After setting up environment variables:

1. ✅ Deploy to Vercel
2. ✅ Verify "AI Active" badge appears
3. ✅ Test chat functionality
4. ✅ Monitor usage in Anthropic console
5. ✅ Consider adding usage tracking/rate limiting if needed

For more information, see:
- Anthropic API Docs: https://docs.anthropic.com/
- Vercel Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables
- Vercel Serverless Functions: https://vercel.com/docs/concepts/functions/serverless-functions
