#!/usr/bin/env python3
"""
HVAC VOICE SALES API
====================
FastAPI server for HVAC voice agent with real-time call management.
Endpoints for initiating calls, processing responses, booking appointments.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import uvicorn

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import core systems
from hvac_voice_agent import HVACVoiceAgent, ProspectContext, CallState
from brain_os import Brain


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class StartCallRequest(BaseModel):
    phone: str = Field(..., description="Prospect phone number")
    name: Optional[str] = Field(None, description="Prospect name")
    company: Optional[str] = Field(None, description="Company name")
    pain_points: List[str] = Field(default_factory=list, description="Known pain points")
    notes: Optional[str] = Field(None, description="Additional context")


class ProcessResponseRequest(BaseModel):
    call_id: str
    response: str = Field(..., description="Prospect's response text")


class BookAppointmentRequest(BaseModel):
    call_id: str
    time_slot: str = Field(..., description="e.g., 'Tuesday at 2:00 PM EST'")
    email: str = Field(..., description="Prospect email")


class EndCallRequest(BaseModel):
    call_id: str
    outcome: str = Field(..., description="won, lost, no_answer, callback")


class CallResponse(BaseModel):
    call_id: str
    phase: str
    agent_message: str
    appointment_booked: bool
    insights: List[str]


# =============================================================================
# APPLICATION STATE
# =============================================================================

class ApplicationState:
    """Global application state"""
    def __init__(self):
        self.brain = Brain()
        self.agent = HVACVoiceAgent(self.brain)
        self.active_calls: Dict[str, CallState] = {}
        self.call_history: List[Dict] = []
        self.websocket_connections: List[WebSocket] = []

        # Load history if exists
        self.history_file = Path("hvac_call_history.json")
        if self.history_file.exists():
            self.call_history = json.loads(self.history_file.read_text())

    def save_history(self):
        """Save call history to disk"""
        self.history_file.write_text(json.dumps(self.call_history, indent=2))

    async def broadcast_update(self, event_type: str, data: Dict):
        """Broadcast update to all connected WebSocket clients"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        dead_connections = []
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except:
                dead_connections.append(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self.websocket_connections.remove(ws)


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="HVAC Voice Sales API",
    description="Multi-AI powered sales agent with real-time call management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
state = ApplicationState()


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """API health check and stats"""
    stats = state.agent.get_stats()
    budget = state.brain.costs.check_budget()

    return {
        "name": "HVAC Voice Sales API",
        "status": "ONLINE",
        "version": "1.0.0",
        "active_calls": len(state.active_calls),
        "total_calls_today": stats["total_calls"],
        "appointments_booked_today": stats["appointments_booked"],
        "conversion_rate": f"{stats['conversion_rate']:.1%}",
        "ai_cost_today": f"${budget['spent']:.4f}",
        "budget_remaining": f"${budget['remaining']:.2f}",
        "performance_multiplier": f"{state.brain.perf:.2%}"
    }


@app.post("/api/calls/start", response_model=CallResponse)
async def start_call(request: StartCallRequest, background_tasks: BackgroundTasks):
    """
    Start a new sales call.

    This initializes the call state and generates the opening greeting.
    """
    try:
        # Create prospect context
        prospect = ProspectContext(
            phone=request.phone,
            name=request.name,
            company=request.company,
            pain_points=request.pain_points
        )

        # Start the call
        call_state = await state.agent.start_call(prospect)

        # Store in active calls
        state.active_calls[call_state.call_id] = call_state

        # Get the agent's opening message
        opening = call_state.transcript[-1]["text"]

        # Broadcast to websockets
        background_tasks.add_task(
            state.broadcast_update,
            "call_started",
            {
                "call_id": call_state.call_id,
                "prospect": request.name or request.phone,
                "message": opening
            }
        )

        return CallResponse(
            call_id=call_state.call_id,
            phase=call_state.phase,
            agent_message=opening,
            appointment_booked=False,
            insights=[]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start call: {str(e)}")


@app.post("/api/calls/respond", response_model=CallResponse)
async def process_response(request: ProcessResponseRequest, background_tasks: BackgroundTasks):
    """
    Process prospect's response and get next agent message.

    This is the core conversation loop - call this each time the prospect speaks.
    """
    call_state = state.active_calls.get(request.call_id)

    if not call_state:
        raise HTTPException(status_code=404, detail=f"Call {request.call_id} not found")

    try:
        # Process the response and get agent's next message
        agent_message = await call_state.process_response(call_state, request.response)

        # Broadcast update
        background_tasks.add_task(
            state.broadcast_update,
            "call_updated",
            {
                "call_id": call_state.call_id,
                "phase": call_state.phase,
                "message": agent_message
            }
        )

        return CallResponse(
            call_id=call_state.call_id,
            phase=call_state.phase,
            agent_message=agent_message,
            appointment_booked=call_state.appointment_booked,
            insights=call_state.insights
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")


@app.post("/api/calls/book")
async def book_appointment(request: BookAppointmentRequest, background_tasks: BackgroundTasks):
    """
    Book an appointment for a prospect.

    Call this when the prospect agrees to a specific time slot.
    """
    call_state = state.active_calls.get(request.call_id)

    if not call_state:
        raise HTTPException(status_code=404, detail=f"Call {request.call_id} not found")

    try:
        booking = await state.agent.book_appointment(
            call_state,
            request.time_slot,
            request.email
        )

        # Broadcast update
        background_tasks.add_task(
            state.broadcast_update,
            "appointment_booked",
            {
                "call_id": call_state.call_id,
                "prospect": call_state.prospect.name,
                "time_slot": request.time_slot,
                "email": request.email
            }
        )

        return booking

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to book appointment: {str(e)}")


@app.post("/api/calls/end")
async def end_call(request: EndCallRequest, background_tasks: BackgroundTasks):
    """
    End a call and log the outcome.

    Outcomes: won (booked), lost (declined), no_answer, callback
    """
    call_state = state.active_calls.get(request.call_id)

    if not call_state:
        raise HTTPException(status_code=404, detail=f"Call {request.call_id} not found")

    try:
        # End the call
        state.agent.end_call(call_state, request.outcome)

        # Move to history
        call_record = {
            "call_id": call_state.call_id,
            "prospect": {
                "name": call_state.prospect.name,
                "phone": call_state.prospect.phone,
                "company": call_state.prospect.company
            },
            "outcome": request.outcome,
            "appointment_booked": call_state.appointment_booked,
            "duration": (call_state.ended_at - call_state.started_at).total_seconds(),
            "phases": [t["phase"] for t in call_state.transcript],
            "insights": call_state.insights,
            "started_at": call_state.started_at.isoformat(),
            "ended_at": call_state.ended_at.isoformat()
        }

        state.call_history.append(call_record)
        state.save_history()

        # Remove from active calls
        del state.active_calls[request.call_id]

        # Broadcast update
        background_tasks.add_task(
            state.broadcast_update,
            "call_ended",
            {
                "call_id": call_state.call_id,
                "outcome": request.outcome
            }
        )

        return {"success": True, "call_record": call_record}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end call: {str(e)}")


@app.get("/api/calls/active")
async def get_active_calls():
    """Get all currently active calls"""
    return {
        "count": len(state.active_calls),
        "calls": [
            {
                "call_id": call_id,
                "prospect": call_state.prospect.name or call_state.prospect.phone,
                "phase": call_state.phase,
                "duration": (datetime.now() - call_state.started_at).total_seconds(),
                "appointment_booked": call_state.appointment_booked
            }
            for call_id, call_state in state.active_calls.items()
        ]
    }


@app.get("/api/calls/history")
async def get_call_history(limit: int = 50):
    """Get call history"""
    return {
        "count": len(state.call_history),
        "calls": state.call_history[-limit:]
    }


@app.get("/api/calls/{call_id}")
async def get_call_details(call_id: str):
    """Get detailed information about a specific call"""
    # Check active calls
    if call_id in state.active_calls:
        call_state = state.active_calls[call_id]
        return {
            "call_id": call_id,
            "status": "active",
            "prospect": {
                "name": call_state.prospect.name,
                "phone": call_state.prospect.phone,
                "company": call_state.prospect.company,
                "pain_points": call_state.prospect.pain_points
            },
            "phase": call_state.phase,
            "transcript": call_state.transcript,
            "insights": call_state.insights,
            "appointment_booked": call_state.appointment_booked,
            "started_at": call_state.started_at.isoformat()
        }

    # Check history
    for call in reversed(state.call_history):
        if call["call_id"] == call_id:
            return {"status": "completed", **call}

    raise HTTPException(status_code=404, detail=f"Call {call_id} not found")


@app.get("/api/stats")
async def get_stats():
    """Get comprehensive statistics"""
    agent_stats = state.agent.get_stats()
    brain_budget = state.brain.costs.check_budget()

    # Calculate today's metrics
    today = datetime.now().date()
    today_calls = [c for c in state.call_history
                   if datetime.fromisoformat(c["started_at"]).date() == today]

    booked_today = len([c for c in today_calls if c["appointment_booked"]])
    revenue_today = booked_today * 200  # $200 per appointment estimate

    return {
        "overview": {
            "total_calls": agent_stats["total_calls"],
            "appointments_booked": agent_stats["appointments_booked"],
            "conversion_rate": agent_stats["conversion_rate"],
            "avg_call_duration": agent_stats["avg_call_duration"],
            "revenue_generated": revenue_today
        },
        "today": {
            "calls": len(today_calls),
            "booked": booked_today,
            "revenue": revenue_today,
            "active_now": len(state.active_calls)
        },
        "ai_performance": {
            "total_requests": agent_stats["ai_provider_stats"]["total_requests"],
            "total_cost": agent_stats["ai_provider_stats"]["total_cost"],
            "budget_spent": brain_budget["spent"],
            "budget_remaining": brain_budget["remaining"]
        },
        "learning": {
            "performance_multiplier": state.brain.perf,
            "winning_patterns": agent_stats["winning_patterns_count"],
            "losing_patterns": agent_stats["losing_patterns_count"]
        }
    }


@app.post("/api/improve")
async def trigger_improvement():
    """
    Manually trigger the 1% improvement cycle.

    Analyzes winning vs losing patterns and identifies improvements.
    """
    try:
        result = await state.agent.improve_from_patterns()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improvement failed: {str(e)}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Dashboard can connect here to receive live updates about calls.
    """
    await websocket.accept()
    state.websocket_connections.append(websocket)

    try:
        # Send initial stats
        stats = await get_stats()
        await websocket.send_json({
            "type": "connected",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })

        # Keep connection alive
        while True:
            # Wait for ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        state.websocket_connections.remove(websocket)


# =============================================================================
# BACKGROUND TASKS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on API startup"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║             HVAC VOICE SALES API - STARTING                   ║
║                                                               ║
║  🎯 Multi-AI Synthesis (Claude + Gemini + GPT)                ║
║  💰 Performance-Based (10% of savings)                        ║
║  📈 Auto-Learning (1% daily improvement)                      ║
║  🔐 Brain OS Integration (security + tracking)                ║
╚═══════════════════════════════════════════════════════════════╝
""")
    print(f"✅ Brain OS initialized (Master Key saved)")
    print(f"✅ HVAC Agent registered")
    print(f"✅ AI Providers configured:")
    config = state.agent.orchestrator.check_config()
    for provider, ready in config.items():
        status = "✓" if ready else "✗"
        print(f"   {status} {provider.upper()}")

    print(f"\n📊 Ready to process calls!")
    print(f"💾 Call history: {len(state.call_history)} previous calls loaded\n")


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("STARTING HVAC VOICE SALES API")
    print("="*60)
    print("\n📖 API Documentation: http://127.0.0.1:8000/docs")
    print("🌐 API Root: http://127.0.0.1:8000")
    print("🔌 WebSocket: ws://127.0.0.1:8000/ws")
    print("\n" + "="*60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
