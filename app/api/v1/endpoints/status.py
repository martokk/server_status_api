from typing import Any

from fastapi import APIRouter

from app.logic.get_statuses import get_all_statuses


# Create a router that bypasses global auth
router = APIRouter(prefix="", include_in_schema=True)

# API_KEY_NAME = "X-API-Key"
# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


# async def get_api_key(
#     api_key_header: Annotated[str | None, Security(api_key_header)],
# ) -> str:
#     """Validate API key from header.

#     Args:
#         api_key_header: API key from request header

#     Returns:
#         Validated API key

#     Raises:
#         HTTPException: If API key is invalid or missing
#     """
#     if not "NOT_IMPLEMENTED_API_KEY":
#         logger.error("EXPORT_API_KEY is not set in environment variables")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Export API key not configured",
#         )

#     # logger.debug(f"Received API key: {api_key_header}")
#     if api_key_header == "NOT_IMPLEMENTED_API_KEY":
#         return api_key_header

#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid API Key",
#     )


@router.get("", include_in_schema=True)
async def get_status() -> dict[str, Any]:
    """Get all statuses.

    Returns:
        Dictionary containing all statuses
    """
    return get_all_statuses()
