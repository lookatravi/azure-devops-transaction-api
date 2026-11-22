"""Synthetic transaction status service for a personal DevOps training lab.

This application uses no real customer or banking data.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("transaction-status")
app = FastAPI(title="NZ Azure DevOps Lab - Transaction Status API", version="1.0.0")

DEMO_TRANSACTIONS = {
    "demo-001": "COMPLETED",
    "demo-002": "PENDING",
    "demo-003": "REJECTED",
}


@app.get("/health/live")
def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness():
    if os.getenv("SIMULATE_OUTAGE", "false").lower() == "true":
        logger.error("Simulated dependency outage: readiness check failed")
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return {"status": "ready"}


@app.get("/api/v1/transactions/{transaction_id}")
def transaction_status(transaction_id: str):
    logger.info("Transaction status lookup requested")
    status = DEMO_TRANSACTIONS.get(transaction_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Demo transaction not found")
    return {
        "transaction_id": transaction_id,
        "status": status,
        "environment": os.getenv("APP_ENV", "local"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }
