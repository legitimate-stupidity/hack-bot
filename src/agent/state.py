"""
State management layer using SQLite for persistence.
Enables long-running tasks and resumption.
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path

DB_PATH = "agent_flow.db"

class PlanStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_FIX = "NEEDS_FIX"

class StateManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        """Initialize the SQLite database schema."""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Plans table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id TEXT PRIMARY KEY,
            prompt TEXT NOT NULL,
            generated_plan TEXT,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Task history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
        );
        """)
        
        # Create indices for performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_plan ON task_history(plan_id);
        """)
        
        conn.commit()
        conn.close()

    def create_plan(self, prompt: str, plan: Dict[str, Any]) -> str:
        """Create a new plan and store it."""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO plans (plan_id, prompt, generated_plan, status) VALUES (?, ?, ?, ?)",
            (plan_id, prompt, json.dumps(plan), PlanStatus.PENDING.value)
        )
        self.add_history(plan_id, "user", prompt)
        conn.commit()
        conn.close()
        return plan_id

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a plan by ID."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plans WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            if data['generated_plan']:
                data['generated_plan'] = json.loads(data['generated_plan'])
            return data
        return None

    def update_plan_status(self, plan_id: str, status: PlanStatus):
        """Update plan status."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plans SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE plan_id = ?",
            (status.value, plan_id)
        )
        conn.commit()
        conn.close()
        self.add_history(plan_id, "system", f"Status updated to {status.value}")

    def update_plan_data(self, plan_id: str, plan: Dict[str, Any]):
        """Update the plan structure."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE plans SET generated_plan = ?, updated_at = CURRENT_TIMESTAMP WHERE plan_id = ?",
            (json.dumps(plan), plan_id)
        )
        conn.commit()
        conn.close()

    def list_plans(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent plans."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plan_id, status, prompt, created_at FROM plans ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_history(self, plan_id: str, role: str, content: str):
        """Add an entry to task history."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO task_history (plan_id, role, content) VALUES (?, ?, ?)",
            (plan_id, role, content)
        )
        conn.commit()
        conn.close()
    
    def get_history(self, plan_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve task history for a plan."""
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if limit:
            cursor.execute(
                "SELECT role, content, timestamp FROM task_history WHERE plan_id = ? ORDER BY timestamp ASC LIMIT ?",
                (plan_id, limit)
            )
        else:
            cursor.execute(
                "SELECT role, content, timestamp FROM task_history WHERE plan_id = ? ORDER BY timestamp ASC",
                (plan_id,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

# Global state manager instance
state = StateManager()
