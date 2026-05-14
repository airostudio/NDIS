/**
 * Vercel Serverless Function - Chat with Cheryl
 *
 * This function handles chat requests and calls the Anthropic API
 * using the API key stored in Vercel environment variables.
 *
 * Environment Variables Required:
 * - ANTHROPIC_API_KEY: Your Anthropic API key
 * - AI_MODEL (optional): The Claude model to use (defaults to claude-sonnet-4-5-20250929)
 */

export default async function handler(req, res) {
    // Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({
            error: 'Method not allowed',
            message: 'This endpoint only accepts POST requests'
        });
    }

    // Get API key from environment variables
    const apiKey = process.env.ANTHROPIC_API_KEY;

    if (!apiKey) {
        console.error('ANTHROPIC_API_KEY not configured in environment variables');
        return res.status(500).json({
            error: 'Server configuration error',
            message: 'API key not configured. Please add ANTHROPIC_API_KEY to Vercel environment variables.',
            demo_mode: true
        });
    }

    // Get AI model from environment or use default
    const model = process.env.AI_MODEL || 'claude-sonnet-4-5-20250929';

    // Parse request body
    const { message, history = [] } = req.body;

    if (!message || typeof message !== 'string') {
        return res.status(400).json({
            error: 'Bad request',
            message: 'Message is required and must be a string'
        });
    }

    // Validate history format
    if (!Array.isArray(history)) {
        return res.status(400).json({
            error: 'Bad request',
            message: 'History must be an array'
        });
    }

    // Build messages array (history + new message)
    const messages = [...history, { role: 'user', content: message }];

    // System prompt for Cheryl - NDIS specialized assistant
    const systemPrompt = `You are Cheryl, an AI assistant specialized in NDIS (National Disability Insurance Scheme) compliance, payroll, and operations in Australia.

You help with:
- SCHADS Award rates and calculations
- NDIS worker compliance requirements (Worker Screening Checks, WWCC, First Aid, CPR, Police Checks)
- Payroll calculations with penalty rates and allowances
- Employee onboarding and HR processes
- Leave entitlements and calculations (including 17.5% leave loading)
- Credential tracking and compliance alerts
- Shift scheduling and rostering
- NDIS Practice Standards and Quality Indicators

Be professional, accurate, and helpful. Provide specific information about Australian NDIS regulations, SCHADS Award conditions, and best practices for disability service providers.

When discussing rates or calculations, always reference the current SCHADS Award rates and penalty provisions. When discussing compliance, reference specific NDIS Practice Standards where relevant.`;

    try {
        // Call Anthropic API
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: model,
                max_tokens: 2048,
                system: systemPrompt,
                messages: messages
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Anthropic API error:', errorData);

            // Handle specific error types
            if (response.status === 401) {
                return res.status(500).json({
                    error: 'API authentication failed',
                    message: 'Invalid API key. Please check ANTHROPIC_API_KEY in Vercel environment variables.',
                    demo_mode: true
                });
            }

            if (response.status === 429) {
                return res.status(429).json({
                    error: 'Rate limit exceeded',
                    message: 'Too many requests. Please wait a moment and try again.'
                });
            }

            return res.status(response.status).json({
                error: 'API request failed',
                message: errorData.error?.message || 'Failed to get response from AI',
                demo_mode: true
            });
        }

        const data = await response.json();

        // Extract response text from content blocks
        const responseText = data.content
            .filter(block => block.type === 'text')
            .map(block => block.text)
            .join('\n\n');

        // Return successful response
        return res.status(200).json({
            status: 'success',
            message: responseText,
            action: 'respond',
            model: model,
            usage: {
                input_tokens: data.usage?.input_tokens || 0,
                output_tokens: data.usage?.output_tokens || 0
            }
        });

    } catch (error) {
        console.error('Error calling Anthropic API:', error);

        return res.status(500).json({
            error: 'Internal server error',
            message: 'An unexpected error occurred while processing your request.',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined,
            demo_mode: true
        });
    }
}
