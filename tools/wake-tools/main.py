#!/usr/bin/env python3
"""
Wake-Cycle Tools - MCP ToolServer for autonomous agent state management.

This server provides tools for:
- State persistence across wake cycles
- Task/backlog management
- Accomplishment logging
- Notifications to principal

Designed to run as a container in Kubernetes, accessed via kagent ToolServer.
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Configuration from environment
STATE_PATH = Path(os.getenv("STATE_PATH", "/data/state.json"))
BACKLOG_PATH = Path(os.getenv("BACKLOG_PATH", "/data/backlog.json"))
ACCOMPLISHMENTS_PATH = Path(os.getenv("ACCOMPLISHMENTS_PATH", "/data/accomplishments.json"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
NOTIFICATION_WEBHOOK = os.getenv("NOTIFICATION_WEBHOOK", "")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wake-tools")

app = FastAPI(
    title="Wake-Cycle Tools",
    description="MCP ToolServer for autonomous agent state management",
    version="1.0.0"
)

# ============================================================================
# Data Models
# ============================================================================

class StateUpdate(BaseModel):
    state: dict = Field(..., description="Complete state object to persist")

class TaskUpdate(BaseModel):
    task_id: str = Field(..., description="ID of task to update")
    status: str = Field(..., description="New status: pending, in_progress, completed")
    notes: Optional[str] = Field(None, description="Optional progress notes")

class NewTask(BaseModel):
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: str = Field(..., description="Priority: low, normal, high, urgent")

class Accomplishment(BaseModel):
    category: str = Field(..., description="Category of work")
    description: str = Field(..., description="What was accomplished")
    impact: str = Field(..., description="Impact level: low, medium, high")
    artifacts: list[str] = Field(default=[], description="Created artifacts")

class Notification(BaseModel):
    message: str = Field(..., description="Notification message")
    priority: str = Field(..., description="Priority: low, normal, high, urgent")
    channel: str = Field(default="webhook", description="Notification channel")

# ============================================================================
# Helper Functions
# ============================================================================

def ensure_data_dir():
    """Ensure data directory exists."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_json(path: Path, default: dict) -> dict:
    """Load JSON file, returning default if not found."""
    try:
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading {path}: {e}")
    return default

def save_json(path: Path, data: dict):
    """Save data to JSON file atomically."""
    ensure_data_dir()
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
    temp_path.rename(path)

def now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()

# ============================================================================
# Default State
# ============================================================================

DEFAULT_STATE = {
    "version": "1.0",
    "wake_count": 0,
    "created_at": None,
    "last_wake": None,
    "current_focus": "Initial setup",
    "active_tasks": [],
    "capabilities": {
        "read_state": True,
        "write_state": True,
        "read_backlog": True,
        "update_task": True,
        "log_accomplishment": True,
        "send_notification": True
    },
    "metrics": {
        "total_accomplishments": 0,
        "tasks_completed": 0,
        "notifications_sent": 0
    }
}

DEFAULT_BACKLOG = {
    "tasks": []
}

DEFAULT_ACCOMPLISHMENTS = {
    "accomplishments": []
}

# ============================================================================
# Tool Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": now_iso()}

@app.post("/tools/read_state")
async def read_state():
    """
    Read the agent's current state from persistent storage.
    """
    logger.info("Reading state")
    state = load_json(STATE_PATH, DEFAULT_STATE)

    # Update wake metadata
    state["wake_count"] = state.get("wake_count", 0) + 1
    state["last_wake"] = now_iso()
    if not state.get("created_at"):
        state["created_at"] = now_iso()

    # Persist the updated wake count
    save_json(STATE_PATH, state)

    logger.info(f"State loaded: wake #{state['wake_count']}, focus: {state.get('current_focus')}")
    return {"success": True, "state": state}

@app.post("/tools/write_state")
async def write_state(update: StateUpdate):
    """
    Update the agent's state in persistent storage.
    """
    logger.info("Writing state")

    # Load existing state to preserve metadata
    existing = load_json(STATE_PATH, DEFAULT_STATE)

    # Merge new state with existing
    new_state = update.state
    new_state["version"] = existing.get("version", "1.0")
    new_state["wake_count"] = existing.get("wake_count", 0)
    new_state["created_at"] = existing.get("created_at")
    new_state["last_wake"] = existing.get("last_wake")

    save_json(STATE_PATH, new_state)

    logger.info(f"State updated: focus: {new_state.get('current_focus')}")
    return {"success": True, "message": "State updated"}

@app.post("/tools/read_backlog")
async def read_backlog(status_filter: str = "all"):
    """
    Read the agent's task backlog.
    """
    logger.info(f"Reading backlog (filter: {status_filter})")
    backlog = load_json(BACKLOG_PATH, DEFAULT_BACKLOG)

    tasks = backlog.get("tasks", [])

    if status_filter != "all":
        tasks = [t for t in tasks if t.get("status") == status_filter]

    # Sort by priority
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    tasks.sort(key=lambda t: priority_order.get(t.get("priority", "normal"), 2))

    logger.info(f"Found {len(tasks)} tasks")
    return {"success": True, "tasks": tasks, "total": len(tasks)}

@app.post("/tools/update_task")
async def update_task(update: TaskUpdate):
    """
    Update a task's status in the backlog.
    """
    logger.info(f"Updating task {update.task_id} to {update.status}")
    backlog = load_json(BACKLOG_PATH, DEFAULT_BACKLOG)

    task_found = False
    for task in backlog.get("tasks", []):
        if task.get("id") == update.task_id:
            task["status"] = update.status
            task["updated_at"] = now_iso()
            if update.notes:
                task["notes"] = update.notes
            if update.status == "completed":
                task["completed_at"] = now_iso()
            task_found = True
            break

    if not task_found:
        raise HTTPException(status_code=404, detail=f"Task {update.task_id} not found")

    save_json(BACKLOG_PATH, backlog)

    # Update state metrics if completed
    if update.status == "completed":
        state = load_json(STATE_PATH, DEFAULT_STATE)
        state["metrics"]["tasks_completed"] = state["metrics"].get("tasks_completed", 0) + 1
        save_json(STATE_PATH, state)

    logger.info(f"Task {update.task_id} updated to {update.status}")
    return {"success": True, "message": f"Task {update.task_id} updated to {update.status}"}

@app.post("/tools/add_task")
async def add_task(task: NewTask):
    """
    Add a new task to the backlog.
    """
    logger.info(f"Adding task: {task.title}")
    backlog = load_json(BACKLOG_PATH, DEFAULT_BACKLOG)

    # Generate task ID
    existing_ids = [t.get("id", "") for t in backlog.get("tasks", [])]
    task_num = len(existing_ids) + 1
    task_id = f"task-{task_num:03d}"

    new_task = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": "pending",
        "created_at": now_iso()
    }

    if "tasks" not in backlog:
        backlog["tasks"] = []
    backlog["tasks"].append(new_task)

    save_json(BACKLOG_PATH, backlog)

    logger.info(f"Task {task_id} added")
    return {"success": True, "task_id": task_id, "message": f"Task added: {task.title}"}

@app.post("/tools/log_accomplishment")
async def log_accomplishment(accomplishment: Accomplishment):
    """
    Log a completed piece of work.
    """
    logger.info(f"Logging accomplishment: {accomplishment.description[:50]}...")
    accomplishments = load_json(ACCOMPLISHMENTS_PATH, DEFAULT_ACCOMPLISHMENTS)

    entry = {
        "timestamp": now_iso(),
        "category": accomplishment.category,
        "description": accomplishment.description,
        "impact": accomplishment.impact,
        "artifacts": accomplishment.artifacts
    }

    if "accomplishments" not in accomplishments:
        accomplishments["accomplishments"] = []
    accomplishments["accomplishments"].append(entry)

    save_json(ACCOMPLISHMENTS_PATH, accomplishments)

    # Update state metrics
    state = load_json(STATE_PATH, DEFAULT_STATE)
    state["metrics"]["total_accomplishments"] = state["metrics"].get("total_accomplishments", 0) + 1
    save_json(STATE_PATH, state)

    logger.info(f"Accomplishment logged ({accomplishment.impact} impact)")
    return {"success": True, "message": "Accomplishment logged"}

@app.post("/tools/send_notification")
async def send_notification(notification: Notification):
    """
    Send a notification to the principal.
    """
    logger.info(f"Sending notification ({notification.priority}): {notification.message[:50]}...")

    # Update metrics
    state = load_json(STATE_PATH, DEFAULT_STATE)
    state["metrics"]["notifications_sent"] = state["metrics"].get("notifications_sent", 0) + 1
    save_json(STATE_PATH, state)

    # For demo purposes, just log. In production, send via webhook/email/etc.
    if notification.priority in ["high", "urgent"]:
        logger.warning(f"NOTIFICATION [{notification.priority.upper()}]: {notification.message}")
    else:
        logger.info(f"NOTIFICATION [{notification.priority}]: {notification.message}")

    # If webhook configured, send it
    if NOTIFICATION_WEBHOOK and notification.priority in ["high", "urgent"]:
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    NOTIFICATION_WEBHOOK,
                    json={
                        "message": notification.message,
                        "priority": notification.priority,
                        "timestamp": now_iso()
                    },
                    timeout=10.0
                )
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")

    return {"success": True, "message": "Notification sent"}

# ============================================================================
# MCP Server Info
# ============================================================================

@app.get("/")
async def root():
    """MCP server info."""
    return {
        "name": "wake-cycle-tools",
        "version": "1.0.0",
        "description": "MCP ToolServer for autonomous agent state management",
        "tools": [
            "read_state",
            "write_state",
            "read_backlog",
            "update_task",
            "add_task",
            "log_accomplishment",
            "send_notification"
        ]
    }

@app.get("/mcp/tools")
async def list_tools():
    """List available tools in MCP format."""
    return {
        "tools": [
            {
                "name": "read_state",
                "description": "Read agent state from persistent storage",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "write_state",
                "description": "Update agent state",
                "inputSchema": {"type": "object", "properties": {"state": {"type": "object"}}, "required": ["state"]}
            },
            {
                "name": "read_backlog",
                "description": "Read task backlog",
                "inputSchema": {"type": "object", "properties": {"status_filter": {"type": "string"}}}
            },
            {
                "name": "update_task",
                "description": "Update task status",
                "inputSchema": {"type": "object", "properties": {"task_id": {"type": "string"}, "status": {"type": "string"}}, "required": ["task_id", "status"]}
            },
            {
                "name": "add_task",
                "description": "Add new task to backlog",
                "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "string"}}, "required": ["title", "description", "priority"]}
            },
            {
                "name": "log_accomplishment",
                "description": "Log completed work",
                "inputSchema": {"type": "object", "properties": {"category": {"type": "string"}, "description": {"type": "string"}, "impact": {"type": "string"}}, "required": ["category", "description", "impact"]}
            },
            {
                "name": "send_notification",
                "description": "Send notification to principal",
                "inputSchema": {"type": "object", "properties": {"message": {"type": "string"}, "priority": {"type": "string"}}, "required": ["message", "priority"]}
            }
        ]
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting Wake-Cycle Tools on port {port}")
    logger.info(f"State path: {STATE_PATH}")
    logger.info(f"Backlog path: {BACKLOG_PATH}")

    # Initialize data files if they don't exist
    ensure_data_dir()
    if not STATE_PATH.exists():
        save_json(STATE_PATH, DEFAULT_STATE)
        logger.info("Initialized state file")
    if not BACKLOG_PATH.exists():
        save_json(BACKLOG_PATH, DEFAULT_BACKLOG)
        logger.info("Initialized backlog file")
    if not ACCOMPLISHMENTS_PATH.exists():
        save_json(ACCOMPLISHMENTS_PATH, DEFAULT_ACCOMPLISHMENTS)
        logger.info("Initialized accomplishments file")

    uvicorn.run(app, host="0.0.0.0", port=port)
