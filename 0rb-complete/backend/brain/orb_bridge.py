#!/usr/bin/env python3
"""
0RB BRIDGE - Integration Layer
===============================
Connects voice input → code generation → deployment.
FastAPI server that orchestrates everything.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import sys

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing systems
from the_instant_creator import InstantCreator
from ai_connectors import AIOrchestrator


# =============================================================================
# MODELS
# =============================================================================

class VoiceToAppRequest(BaseModel):
    """Voice/text intent → deployed app"""
    intent: str
    user_id: str = "default"
    deployment_target: str = "vercel"  # vercel, railway, docker


class BuildResult(BaseModel):
    """Build result"""
    build_id: str
    intent: str
    status: str
    love_score: float
    net_positive: bool
    code_file: Optional[str]
    deployment_url: Optional[str]
    created_at: str


# =============================================================================
# APPLICATION STATE
# =============================================================================

class BridgeState:
    """Global application state"""
    def __init__(self):
        self.creator = InstantCreator()
        self.builds: Dict[str, Dict] = {}
        self.websocket_connections: List[WebSocket] = []

        # Load previous builds
        self.builds_file = Path("builds_history.json")
        if self.builds_file.exists():
            self.builds = json.loads(self.builds_file.read_text())

    def save_builds(self):
        """Save builds to disk"""
        self.builds_file.write_text(json.dumps(self.builds, indent=2))

    async def broadcast(self, event_type: str, data: Dict):
        """Broadcast to all connected websockets"""
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

        for ws in dead_connections:
            self.websocket_connections.remove(ws)


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="0RB Bridge",
    description="Voice/Text → Deployed App in Minutes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = BridgeState()


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "name": "0RB Bridge",
        "status": "ONLINE",
        "version": "1.0.0",
        "builds": len(state.builds),
        "love_ledger": state.creator.love_ledger.get_total_love()
    }


@app.post("/voice-to-app", response_model=BuildResult)
async def voice_to_app(
    request: VoiceToAppRequest,
    background_tasks: BackgroundTasks
):
    """
    Main endpoint: Voice/text intent → deployed app

    This orchestrates the entire flow:
    1. Validate intent (GCODE)
    2. Generate code (InstantCreator)
    3. Deploy (Vercel/Railway)
    4. Return result
    """
    print(f"\n🎤 Received intent: {request.intent[:50]}...")

    # Broadcast start
    background_tasks.add_task(
        state.broadcast,
        "build_started",
        {"intent": request.intent, "user": request.user_id}
    )

    try:
        # Use InstantCreator to generate system
        result = await state.creator.create(request.intent)

        # Create build record
        build_id = f"BUILD-{int(datetime.now().timestamp())}"

        build_record = {
            "build_id": build_id,
            "intent": request.intent,
            "status": "completed" if result["success"] else "failed",
            "love_score": result.get("love_score", 0),
            "net_positive": result.get("net_positive", False),
            "code_file": result.get("code_file"),
            "deployment_url": None,  # TODO: Actual deployment
            "created_at": datetime.now().isoformat(),
            "user_id": request.user_id
        }

        # Save build
        state.builds[build_id] = build_record
        state.save_builds()

        # Broadcast completion
        background_tasks.add_task(
            state.broadcast,
            "build_completed",
            build_record
        )

        return BuildResult(**build_record)

    except Exception as e:
        print(f"❌ Build failed: {e}")

        build_record = {
            "build_id": f"BUILD-{int(datetime.now().timestamp())}",
            "intent": request.intent,
            "status": "failed",
            "love_score": 0,
            "net_positive": False,
            "code_file": None,
            "deployment_url": None,
            "created_at": datetime.now().isoformat(),
            "error": str(e)
        }

        state.builds[build_record["build_id"]] = build_record
        state.save_builds()

        return BuildResult(**build_record)


@app.post("/text-to-app", response_model=BuildResult)
async def text_to_app(
    request: VoiceToAppRequest,
    background_tasks: BackgroundTasks
):
    """Alias for voice-to-app (same functionality)"""
    return await voice_to_app(request, background_tasks)


@app.get("/builds")
async def get_builds(limit: int = 50):
    """Get recent builds"""
    builds_list = list(state.builds.values())
    builds_list.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "total": len(state.builds),
        "builds": builds_list[:limit]
    }


@app.get("/builds/{build_id}")
async def get_build(build_id: str):
    """Get specific build"""
    build = state.builds.get(build_id)

    if not build:
        return {"error": "Build not found"}, 404

    return build


@app.post("/replicate/{pattern_id}")
async def replicate_pattern(
    pattern_id: str,
    background_tasks: BackgroundTasks
):
    """
    Replicate a successful pattern.

    Takes a successful build and creates variations.
    """
    # Find pattern
    pattern = None
    for build in state.builds.values():
        if build.get("love_score", 0) > 0.85:  # High love patterns
            pattern = build
            break

    if not pattern:
        return {"error": "No high-love patterns found"}, 404

    # Create variation intent
    variation_intent = f"Build improved version of {pattern['intent']} with enhanced features"

    # Generate variation
    result = await state.creator.create(variation_intent)

    return {
        "original_pattern": pattern_id,
        "variation": result
    }


@app.get("/stats")
async def get_stats():
    """Get comprehensive statistics"""
    love_report = state.creator.get_love_report()

    # Calculate build stats
    total_builds = len(state.builds)
    successful = len([b for b in state.builds.values() if b["status"] == "completed"])
    high_love = len([b for b in state.builds.values() if b.get("love_score", 0) > 0.85])

    return {
        "builds": {
            "total": total_builds,
            "successful": successful,
            "success_rate": successful / total_builds if total_builds > 0 else 0,
            "high_love_count": high_love
        },
        "love_report": love_report,
        "performance_multiplier": state.creator.brain.perf
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time updates.

    Dashboard connects here to receive build progress.
    """
    await websocket.accept()
    state.websocket_connections.append(websocket)

    try:
        # Send current stats
        stats = await get_stats()
        await websocket.send_json({
            "type": "connected",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })

        # Keep alive
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        state.websocket_connections.remove(websocket)


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    0RB BRIDGE - STARTING                      ║
║                                                               ║
║  Voice/Text → Deployed App                                   ║
║  Real-time WebSocket Updates                                 ║
║  Love-Driven Code Generation                                 ║
║                                                               ║
║  Endpoints:                                                  ║
║    POST /voice-to-app - Main endpoint                        ║
║    POST /text-to-app - Alias                                 ║
║    GET  /builds - List builds                                ║
║    WS   /ws - Real-time updates                              ║
╚═══════════════════════════════════════════════════════════════╝
""")

    print(f"✅ InstantCreator loaded")
    print(f"💾 Previous builds: {len(state.builds)}")
    print(f"💝 Love accumulated: {state.creator.love_ledger.get_total_love()['total_love']:.2f}")
    print()


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("STARTING 0RB BRIDGE")
    print("="*60)
    print("\n📖 API Docs: http://localhost:8080/docs")
    print("🌐 API Root: http://localhost:8080")
    print("🔌 WebSocket: ws://localhost:8080/ws")
    print("\n" + "="*60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
