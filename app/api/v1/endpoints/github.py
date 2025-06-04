import json

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse

from app import logger
from app.services.github_deploy import trigger_netcat_listener, verify_signature


router = APIRouter()


@router.post("/github-deploy")
async def github_deploy_webhook(request: Request) -> JSONResponse:
    """Handle GitHub webhook requests."""
    try:
        # Convert headers to dict for easier handling
        headers = dict(request.headers)

        # Read payload first so we have it for signature verification
        payload = await request.body()

        # Verify signature using all headers
        if not verify_signature(payload, headers):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Get event type, checking multiple possible header names
        event_type = (
            headers.get("X-GitHub-Event")
            or headers.get("x-github-event")
            or headers.get("HTTP_X_GITHUB_EVENT")
        )

        if not event_type:
            raise HTTPException(status_code=400, detail="Missing GitHub event type")

        # Only proceed if this is a deployment event
        if event_type != "deployment":
            return JSONResponse(
                content={"status": "skipped", "message": f"Not a deployment event: {event_type}"},
                status_code=200,
            )

        # Parse the payload
        payload_json = json.loads(payload)
        if payload_json.get("deployment", {}).get("environment") != "production":
            return JSONResponse(
                content={"status": "skipped", "message": "Not a production deployment"},
                status_code=200,
            )

        # Execute the deployment script with debug info
        logger.info("Triggering deployment via netcat listener")
        return trigger_netcat_listener()

    except HTTPException as e:
        logger.error(f"HTTP Exception in webhook: {str(e.detail)}")
        return JSONResponse(
            content={"status": "error", "message": str(e.detail)}, status_code=e.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": f"Internal server error: {str(e)}"},
            status_code=500,
        )
