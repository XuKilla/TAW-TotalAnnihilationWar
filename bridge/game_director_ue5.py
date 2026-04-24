"""
GAME DIRECTOR AI — UE5 Console Interface
Run this from UE5 Python console or Editor Utility Widget
Talks to bridge_v212.py Game Director endpoint

USAGE:
  ask_director("design a mimic enemy class for TAW")
  ask_director("generate a blueprint for DemanKhan abilities")
  ask_director("how should larva stage 3 fight?")
"""

import unreal
import urllib.request
import urllib.parse
import json

# Bridge endpoint — update IP if needed
BRIDGE_URL = "http://127.0.0.1:30011/gamedirector/chat"

# Conversation history — persists during session
_conversation_history = []


def ask_director(message):
    """
    Ask the Game Director AI a question from UE5.
    
    Examples:
        ask_director("design a TAW mimic enemy")
        ask_director("create blueprint for freestyle CQC input mapping")
        ask_director("how should hybrid guardians behave in phase 2?")
    """
    global _conversation_history

    unreal.log(f"[GAME DIRECTOR] You: {message}")

    payload = json.dumps({
        "message": message,
        "history": _conversation_history
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            BRIDGE_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            reply = data.get("response", "No response received")

            # Store in history
            _conversation_history.append({"role": "user", "content": message})
            _conversation_history.append({"role": "assistant", "content": reply})

            # Keep last 20 messages
            if len(_conversation_history) > 20:
                _conversation_history = _conversation_history[-20:]

            # Print to UE5 log
            unreal.log("=" * 60)
            unreal.log("[GAME DIRECTOR AI]")
            unreal.log("=" * 60)

            # Print in chunks (UE5 log has line limits)
            lines = reply.split("\n")
            for line in lines:
                if line.strip():
                    unreal.log(line)

            unreal.log("=" * 60)
            return reply

    except Exception as e:
        error_msg = f"[GAME DIRECTOR] ERROR: {str(e)}"
        unreal.log_error(error_msg)
        unreal.log_error("Make sure bridge_v212.py is running on port 30011")
        return error_msg


def clear_history():
    """Clear conversation history to start fresh"""
    global _conversation_history
    _conversation_history = []
    unreal.log("[GAME DIRECTOR] Conversation history cleared.")


def director_status():
    """Check if Game Director AI is reachable"""
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:30011/health",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            unreal.log(f"[GAME DIRECTOR] Bridge status: {data.get('status', 'unknown')}")
            unreal.log("[GAME DIRECTOR] Game Director AI is READY")
            return True
    except Exception as e:
        unreal.log_error(f"[GAME DIRECTOR] Bridge unreachable: {str(e)}")
        return False


# Auto-announce on load
unreal.log("=" * 60)
unreal.log("GAME DIRECTOR AI — UE5 Interface Loaded")
unreal.log("Commands:")
unreal.log("  ask_director('your question here')")
unreal.log("  clear_history()")
unreal.log("  director_status()")
unreal.log("=" * 60)
