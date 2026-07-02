from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn
from app.agent import chat

app = FastAPI(title="SHL Assessment Recommender Agent")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>SHL Assessment Recommender</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .container { width: 700px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #00A651; padding: 20px; text-align: center; color: white; }
        .header h1 { font-size: 22px; }
        .header p { font-size: 13px; opacity: 0.9; margin-top: 5px; }
        .chat-box { height: 450px; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
        .message { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
        .user { background: #00A651; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .agent { background: #f0f2f5; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; }
        .recommendations { margin-top: 10px; }
        .rec-item { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 8px 12px; margin-top: 6px; font-size: 13px; }
        .rec-item a { color: #00A651; text-decoration: none; font-weight: bold; }
        .rec-item a:hover { text-decoration: underline; }
        .rec-type { color: #888; font-size: 11px; margin-top: 2px; }
        .input-area { padding: 16px; border-top: 1px solid #eee; display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        .input-area input:focus { border-color: #00A651; }
        .input-area button { background: #00A651; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold; }
        .input-area button:hover { background: #008c44; }
        .input-area button:disabled { background: #ccc; cursor: not-allowed; }
        .typing { color: #888; font-size: 13px; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SHL Assessment Recommender</h1>
            <p>Tell me about the role you are hiring for and I will recommend the right assessments</p>
        </div>
        <div class="chat-box" id="chatBox">
            <div class="message agent">
                Hello! I am the SHL Assessment Recommender. Tell me about the role you are hiring for and I will suggest the most suitable assessments from the SHL catalog.
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="e.g. I am hiring a mid-level Java developer..." onkeypress="handleKey(event)" />
            <button onclick="sendMessage()" id="sendBtn">Send</button>
        </div>
    </div>

    <script>
        let conversationHistory = [];

        function handleKey(event) {
            if (event.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const chatBox = document.getElementById('chatBox');
            const userText = input.value.trim();
            if (!userText) return;

            // Add user message
            conversationHistory.push({ role: 'user', content: userText });
            chatBox.innerHTML += `<div class="message user">${userText}</div>`;
            input.value = '';
            sendBtn.disabled = true;

            // Show typing
            chatBox.innerHTML += `<div class="message agent typing" id="typing">Thinking...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: conversationHistory })
                });
                const data = await response.json();

                // Remove typing
                document.getElementById('typing').remove();

                // Build agent message
                let agentHTML = `<div class="message agent">${data.reply}`;

                if (data.recommendations && data.recommendations.length > 0) {
                    agentHTML += `<div class="recommendations">`;
                    data.recommendations.forEach((rec, i) => {
                        agentHTML += `
                            <div class="rec-item">
                                <a href="${rec.url}" target="_blank">${i+1}. ${rec.name}</a>
                                <div class="rec-type">${rec.test_type}</div>
                            </div>`;
                    });
                    agentHTML += `</div>`;
                }
                agentHTML += `</div>`;
                chatBox.innerHTML += agentHTML;

                // Add to history
                conversationHistory.push({ role: 'assistant', content: data.reply });
                chatBox.scrollTop = chatBox.scrollHeight;

            } catch (error) {
                document.getElementById('typing').remove();
                chatBox.innerHTML += `<div class="message agent">Sorry, something went wrong. Please try again.</div>`;
            }
            sendBtn.disabled = false;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]
        result = chat(messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860, reload=False)