import hashlib
import hmac
import os
import socket

from app import logger
from starlette.responses import JSONResponse

os.environ["ENV_FILE"] = "app/data/.env"

GITHUB_DEPLOY_WEBHOOK = os.getenv("GITHUB_DEPLOY_WEBHOOK")
DOCKER_HOST = os.getenv("DOCKER_HOST")
NETCAT_PORT = os.getenv("NETCAT_PORT")


def verify_signature(payload: bytes, request_headers: dict[str, str]) -> bool:
    """Verify that the webhook payload was sent by GitHub."""

    # Try different possible header names for the signature
    signature = (
        request_headers.get("X-Hub-Signature-256")
        or request_headers.get("x-hub-signature-256")
        or request_headers.get("HTTP_X_HUB_SIGNATURE_256")
    )

    if not signature:
        logger.error("No signature found in any expected headers")
        return False

    if not GITHUB_DEPLOY_WEBHOOK:
        logger.error("GITHUB_DEPLOY_WEBHOOK is not set in environment")
        return False

    try:
        # Remove 'sha256=' prefix if present
        signature = signature.replace("sha256=", "")

        # Calculate expected signature
        expected_signature = hmac.new(
            GITHUB_DEPLOY_WEBHOOK.encode(), payload, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False


def trigger_netcat_listener() -> JSONResponse:
    """Trigger the netcat listener to restart the containers."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Set a 5-second timeout
            s.connect((DOCKER_HOST, NETCAT_PORT))
            s.sendall(b"trigger\n")  # Send with a newline

            # Optional: If a response is not expected, skip s.recv(1024)
            try:
                response = s.recv(1024).decode()  # Attempt to receive a response
                return JSONResponse(
                    content={"status": "success", "message": response},
                    status_code=200,
                )
            except TimeoutError:
                # Log warning and proceed if no response is expected
                logger.warning(
                    f"No response received from netcat listener on "
                    f"{DOCKER_HOST}:{NETCAT_PORT}"
                )
                return JSONResponse(
                    content={
                        "status": "success",
                        "message": "Triggered successfully, no response received",
                    },
                    status_code=200,
                )
    except TimeoutError:
        logger.error(f"Connection timed out to {DOCKER_HOST}:{NETCAT_PORT}")
        return JSONResponse(
            content={"status": "error", "message": "Connection timed out"},
            status_code=500,
        )
    except Exception as e:
        logger.error(f"Failed to trigger netcat listener: {str(e)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Failed to trigger netcat listener: {str(e)}",
            },
            status_code=500,
        )
