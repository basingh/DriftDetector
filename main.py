#!/usr/bin/env python3
"""
Main entry point for the drift detection application.
Provides both CLI and web interface functionality.
"""
import sys
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from drift_detector.cli import main as cli_main
from drift_detector.get_state import run_get_state
from drift_detector.get_drift import run_get_drift

# Create Flask app for web interface
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Create necessary directories for templates and static files
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Global variable to store results
last_results = {
    "get_state": None,
    "get_drift": None,
    "timestamp": None
}

@app.route("/")
def index():
    """Main page that provides interface to CLI commands."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drift Detector</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="mb-4">Drift Detector</h1>
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">Get State</div>
                        <div class="card-body">
                            <p>Retrieve cartography state files from the infrastructure.</p>
                            <form action="/run-get-state" method="post">
                                <div class="mb-3">
                                    <label for="base_path" class="form-label">Base Path</label>
                                    <input type="text" class="form-control" id="base_path" name="base_path" 
                                           value="/path/to/base/directory" required>
                                </div>
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="verbose" name="verbose">
                                    <label class="form-check-label" for="verbose">Verbose Logging</label>
                                </div>
                                <button type="submit" class="btn btn-primary">Run</button>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">Get Drift</div>
                        <div class="card-body">
                            <p>Detect drift in cartography state files.</p>
                            <form action="/run-get-drift" method="post">
                                <div class="mb-3">
                                    <label for="base_path_drift" class="form-label">Base Path</label>
                                    <input type="text" class="form-control" id="base_path_drift" name="base_path" 
                                           value="/path/to/base/directory" required>
                                </div>
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="verbose_drift" name="verbose">
                                    <label class="form-check-label" for="verbose_drift">Verbose Logging</label>
                                </div>
                                <button type="submit" class="btn btn-primary">Run</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">Results</div>
                <div class="card-body">
                    <pre id="results-output">No results yet. Run a command to see output.</pre>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/run-get-state", methods=["POST"])
def run_get_state_web():
    """Run the get-state command from web interface."""
    base_path = request.form.get("base_path", "/path/to/base/directory")
    verbose = "verbose" in request.form
    
    try:
        # Run the get_state function directly
        result = run_get_state(base_path)
        
        # Store results
        last_results["get_state"] = result
        last_results["timestamp"] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "result": result,
            "message": "Successfully ran get-state command."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error running get-state command."
        })

@app.route("/run-get-drift", methods=["POST"])
def run_get_drift_web():
    """Run the get-drift command from web interface."""
    base_path = request.form.get("base_path", "/path/to/base/directory")
    verbose = "verbose" in request.form
    
    try:
        # Run the get_drift function directly
        result = run_get_drift(base_path)
        
        # Store results
        last_results["get_drift"] = result
        last_results["timestamp"] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "result": result,
            "message": "Successfully ran get-drift command."
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error running get-drift command."
        })

@app.route("/results")
def view_results():
    """View the results of the last command."""
    return jsonify(last_results)

# Main entry point for CLI
if __name__ == "__main__":
    sys.exit(cli_main())
