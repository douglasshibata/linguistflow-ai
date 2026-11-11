"""Structural smoke test — verifies key files for the unified Python backend."""

import os
import sys


def check_api() -> bool:
    print("Checking API (Python unified backend)...")
    root = "linguistflow-ai/api"
    required = [
        "app/main.py",
        "app/config.py",
        "app/deps.py",
        "app/llm/router.py",
        "app/llm/registry.py",
        "app/lessons/routes.py",
        "app/speech/routes.py",
        "app/db/mongo.py",
        "app/db/neo4j.py",
        "app/security/headers.py",
        "app/security/rate_limit.py",
        "requirements.txt",
        "Dockerfile",
    ]
    missing = [p for p in required if not os.path.exists(os.path.join(root, p))]
    if missing:
        print(f"  MISSING: {missing}")
        return False
    for p in required:
        print(f"  OK {p}")
    return True


def check_no_legacy() -> bool:
    print("\nChecking legacy folders are gone...")
    legacy = ["linguistflow-ai/backend", "linguistflow-ai/ai-engine"]
    leftover = [p for p in legacy if os.path.exists(p)]
    if leftover:
        print(f"  STILL PRESENT: {leftover}")
        return False
    print("  OK: backend/ and ai-engine/ removed")
    return True


def check_frontend() -> bool:
    print("\nChecking Frontend...")
    if not os.path.exists("linguistflow-ai/frontend/app.py"):
        print("  MISSING app.py")
        return False
    print("  OK frontend/app.py")
    return True


def check_demo() -> bool:
    print("\nChecking Demo assets...")
    paths = [
        "linguistflow-ai/demo/demo.sh",
        "linguistflow-ai/demo/presentation.html",
        "linguistflow-ai/demo/LOCAL_OLLAMA_TUTORIAL.md",
    ]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print(f"  MISSING: {missing}")
        return False
    for p in paths:
        print(f"  OK {p}")
    return True


def check_compose_env() -> bool:
    print("\nChecking root files...")
    paths = [
        "linguistflow-ai/docker-compose.yml",
        "linguistflow-ai/.env.example",
        "linguistflow-ai/README.md",
        "linguistflow-ai/CLAUDE.md",
    ]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print(f"  MISSING: {missing}")
        return False
    for p in paths:
        print(f"  OK {p}")
    return True


if __name__ == "__main__":
    results = [
        check_api(),
        check_no_legacy(),
        check_frontend(),
        check_demo(),
        check_compose_env(),
    ]
    if all(results):
        print("\nSmoke test passed: project structure looks correct.")
    else:
        print("\nSmoke test FAILED.")
        sys.exit(1)
