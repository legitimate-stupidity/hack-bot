"""
LLM Provider - Simulates or interfaces with language models.
"""
import asyncio
import json
import textwrap
from typing import Dict, Any

class LLMProvider:
    """Manages interaction with language models using structured JSON output."""
    
    async def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a JSON-structured response from the LLM.
        In production, this would call Gemini or another API.
        """
        await asyncio.sleep(0.1)  # Simulate latency
        
        # Demonstrate different responses based on prompt content
        if "generate a structured plan" in prompt.lower():
            return self._simulate_planning(prompt)
        elif "fix" in prompt.lower() or "error" in prompt.lower():
            return self._simulate_correction(prompt)
        elif "flask" in prompt.lower():
            return self._get_flask_plan()
        
        # Default response
        return {
            "thought": "Generic task detected",
            "steps": [{"tool": "list_files", "args": {"path": "."}}]
        }

    def _simulate_planning(self, prompt: str) -> Dict[str, Any]:
        """Simulate planning for various common tasks."""
        if "flask" in prompt.lower() or "/health" in prompt.lower():
            return self._get_flask_plan()
        elif "node" in prompt.lower():
            return self._get_node_plan()
        elif "list" in prompt.lower():
            return {
                "thought": "User wants to list files",
                "steps": [{"tool": "list_files", "args": {"path": "."}}]
            }
        
        return {
            "thought": "Analyzing task requirements",
            "steps": [{"tool": "run_shell", "args": {"command": "pwd"}}]
        }

    def _simulate_correction(self, prompt: str) -> Dict[str, Any]:
        """Simulate error correction."""
        if "modulenotfounderror" in prompt.lower() or "no module" in prompt.lower():
            return {
                "thought": "Module import error detected. Fixing imports.",
                "steps": [
                    {"tool": "write_file", "args": {
                        "path": "app.py",
                        "content": self._get_fixed_flask_code()
                    }},
                    {"tool": "run_shell", "args": {"command": "pytest test_app.py"}, "is_verification": True}
                ]
            }
        
        return {
            "thought": "Error analysis: attempting recovery",
            "steps": [{"tool": "run_shell", "args": {"command": "python --version"}}]
        }

    def _get_flask_plan(self) -> Dict[str, Any]:
        """Plan for creating a Flask app."""
        return {
            "thought": "User wants a Flask app with /health endpoint. I'll install dependencies, create app.py, create tests, and verify functionality.",
            "steps": [
                {
                    "tool": "run_shell",
                    "args": {"command": "pip install flask pytest"}
                },
                {
                    "tool": "write_file",
                    "args": {
                        "path": "app.py",
                        "content": self._get_flask_code()
                    }
                },
                {
                    "tool": "write_file",
                    "args": {
                        "path": "test_app.py",
                        "content": self._get_test_code()
                    }
                },
                {
                    "tool": "run_shell",
                    "args": {"command": "pytest test_app.py -v"},
                    "is_verification": True
                }
            ]
        }

    def _get_node_plan(self) -> Dict[str, Any]:
        """Plan for creating a Node.js app."""
        return {
            "thought": "User wants a Node.js app. I'll set up npm and create a basic server.",
            "steps": [
                {
                    "tool": "run_shell",
                    "args": {"command": "npm init -y"}
                },
                {
                    "tool": "run_shell",
                    "args": {"command": "npm install express"}
                },
                {
                    "tool": "write_file",
                    "args": {
                        "path": "server.js",
                        "content": textwrap.dedent("""
                            const express = require('express');
                            const app = express();
                            const PORT = 3000;
                            
                            app.get('/health', (req, res) => {
                                res.json({ status: 'ok' });
                            });
                            
                            app.listen(PORT, () => {
                                console.log(`Server running on port ${PORT}`);
                            });
                        """).strip()
                    }
                }
            ]
        }

    def _get_flask_code(self) -> str:
        """Returns Flask app code."""
        return textwrap.dedent("""
            from flask import Flask, jsonify
            
            app = Flask(__name__)
            
            @app.route('/health')
            def health():
                return jsonify({'status': 'ok'}), 200
            
            if __name__ == '__main__':
                app.run(debug=True)
        """).strip()

    def _get_fixed_flask_code(self) -> str:
        """Returns corrected Flask code."""
        return self._get_flask_code()  # Same as above for this demo

    def _get_test_code(self) -> str:
        """Returns test code for Flask app."""
        return textwrap.dedent("""
            import pytest
            from app import app
            
            @pytest.fixture
            def client():
                app.config['TESTING'] = True
                with app.test_client() as client:
                    yield client
            
            def test_health_endpoint(client):
                response = client.get('/health')
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'ok'
        """).strip()

# Global LLM instance
llm = LLMProvider()
