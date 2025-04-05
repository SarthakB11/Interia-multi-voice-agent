from fastapi import FastAPI, Request
from .n8n_handlers import N8NWorkflowHandler

app = FastAPI()
workflow_handler = N8NWorkflowHandler()

@app.post("/webhook/call-result")
async def handle_call_result(request: Request):
    """Handle webhook callbacks from Vapi with call results."""
    webhook_data = await request.json()
    workflow_handler.handle_call_result(webhook_data)
    return {"status": "success"}

@app.post("/trigger/outbound-calls")
async def trigger_outbound_calls():
    """Endpoint to trigger outbound calls."""
    workflow_handler.handle_trigger_workflow()
    return {"status": "success"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 