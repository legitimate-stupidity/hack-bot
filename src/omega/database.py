"""
OMEGA Database Manager Module
Complete implementation extracted from .build file (lines 2816-2844)
Provides SQLite-based target management and data persistence.
"""

import sqlite3
import random
from typing import Optional, List, Tuple


class DatabaseManager:
    """
    SQLite-based database manager for OMEGA framework.
    Handles target storage, vulnerability data, and persistence.
    """
    
    def __init__(self, db_path: str = ':memory:'):
        """
        Initialize database connection and schema.
        
        Args:
            db_path: Path to SQLite database file (default: in-memory)
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._initialize_db()
    
    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"[ERROR] Database connection failed: {e}")
            self.conn = None
    
    def _initialize_db(self) -> None:
        """Initialize database schema."""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        try:
            # Targets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY,
                    ip_address TEXT UNIQUE NOT NULL,
                    hostname TEXT,
                    port INTEGER,
                    service TEXT,
                    os_type TEXT,
                    status TEXT DEFAULT 'active',
                    last_scanned TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Vulnerabilities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY,
                    target_id INTEGER NOT NULL,
                    cve_id TEXT,
                    severity TEXT,
                    description TEXT,
                    exploit_available INTEGER DEFAULT 0,
                    confirmed INTEGER DEFAULT 0,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(target_id) REFERENCES targets(id)
                )
            """)
            
            # Exploit history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exploit_history (
                    id INTEGER PRIMARY KEY,
                    target_id INTEGER NOT NULL,
                    vuln_id INTEGER,
                    exploit_type TEXT,
                    status TEXT,
                    result TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(target_id) REFERENCES targets(id),
                    FOREIGN KEY(vuln_id) REFERENCES vulnerabilities(id)
                )
            """)
            
            # Session data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_data (
                    id INTEGER PRIMARY KEY,
                    target_id INTEGER NOT NULL,
                    session_key TEXT UNIQUE,
                    auth_method TEXT,
                    credentials TEXT,
                    access_level TEXT,
                    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(target_id) REFERENCES targets(id)
                )
            """)
            
            # Create indices for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_targets_ip ON targets(ip_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vuln_target ON vulnerabilities(target_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exploit_target ON exploit_history(target_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_target ON session_data(target_id)")
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"[ERROR] Database initialization failed: {e}")
            if self.conn:
                self.conn.rollback()
    
    def add_target(self, ip_address: str, hostname: str = "", port: int = 0, 
                   service: str = "", os_type: str = "") -> int:
        """
        Add a target to the database.
        
        Args:
            ip_address: Target IP address
            hostname: Optional hostname
            port: Optional port number
            service: Optional service name
            os_type: Optional OS type
            
        Returns:
            Target ID if successful, -1 on failure
        """
        if not self.conn:
            return -1
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO targets (ip_address, hostname, port, service, os_type)
                VALUES (?, ?, ?, ?, ?)
            """, (ip_address, hostname, port, service, os_type))
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # Target already exists, return its ID
            return self.get_target_id(ip_address)
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to add target: {e}")
            return -1
    
    def get_target_id(self, ip_address: str) -> int:
        """Get target ID by IP address."""
        if not self.conn:
            return -1
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id FROM targets WHERE ip_address = ?", (ip_address,))
            result = cursor.fetchone()
            return result[0] if result else -1
        except sqlite3.Error:
            return -1
    
    def get_target(self, target_id: int) -> Optional[dict]:
        """Get target details by ID."""
        if not self.conn:
            return None
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM targets WHERE id = ?", (target_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error:
            return None
    
    def list_targets(self, status: Optional[str] = None) -> List[dict]:
        """List all targets, optionally filtered by status."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        try:
            if status:
                cursor.execute("SELECT * FROM targets WHERE status = ?", (status,))
            else:
                cursor.execute("SELECT * FROM targets")
            
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def update_target_status(self, target_id: int, status: str) -> bool:
        """Update target status."""
        if not self.conn:
            return False
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE targets SET status = ?, last_scanned = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, target_id))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False
    
    def add_vulnerability(self, target_id: int, cve_id: str, severity: str,
                         description: str = "", exploit_available: int = 0) -> int:
        """Add vulnerability record."""
        if not self.conn:
            return -1
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO vulnerabilities (target_id, cve_id, severity, description, exploit_available)
                VALUES (?, ?, ?, ?, ?)
            """, (target_id, cve_id, severity, description, exploit_available))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to add vulnerability: {e}")
            return -1
    
    def get_vulnerabilities(self, target_id: int) -> List[dict]:
        """Get all vulnerabilities for a target."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM vulnerabilities WHERE target_id = ?
                ORDER BY severity DESC
            """, (target_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def add_exploit_attempt(self, target_id: int, exploit_type: str, 
                           status: str, result: str = "") -> int:
        """Record an exploit attempt."""
        if not self.conn:
            return -1
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO exploit_history (target_id, exploit_type, status, result)
                VALUES (?, ?, ?, ?)
            """, (target_id, exploit_type, status, result))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error:
            return -1
    
    def get_exploit_history(self, target_id: int, limit: int = 50) -> List[dict]:
        """Get exploit history for a target."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM exploit_history WHERE target_id = ?
                ORDER BY executed_at DESC LIMIT ?
            """, (target_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def add_session(self, target_id: int, session_key: str, auth_method: str,
                   credentials: str = "", access_level: str = "user") -> int:
        """Record established session/access."""
        if not self.conn:
            return -1
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO session_data (target_id, session_key, auth_method, credentials, access_level)
                VALUES (?, ?, ?, ?, ?)
            """, (target_id, session_key, auth_method, credentials, access_level))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error:
            return -1
    
    def get_sessions(self, target_id: int) -> List[dict]:
        """Get all sessions for a target."""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, target_id, auth_method, access_level, established_at
                FROM session_data WHERE target_id = ?
                ORDER BY established_at DESC
            """, (target_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def execute_query(self, query: str, params: Tuple = ()) -> Optional[List[dict]]:
        """Execute arbitrary query (use with caution)."""
        if not self.conn:
            return None
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"[ERROR] Query execution failed: {e}")
            return None
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.close()


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_database(db_path: str = ':memory:') -> DatabaseManager:
    """Get or create global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
    return _db_instance


def close_database() -> None:
    """Close global database instance."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
