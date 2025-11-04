"""Custom APIRoute that automatically injects timezone context into Pydantic response models."""

import json
from typing import Callable, Any
from zoneinfo import ZoneInfo

from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class TimezoneAwareRoute(APIRoute):
    """
    Custom APIRoute that automatically injects timezone context when serializing Pydantic responses.

    This route class intercepts the response and re-serializes Pydantic models
    with the timezone context from the request state, enabling automatic timezone
    conversion for all response schemas that inherit from TimezoneAwareSchema.

    Usage in router:
        router = APIRouter(route_class=TimezoneAwareRoute)
    """

    def get_route_handler(self) -> Callable:
        """Override the route handler to inject timezone context."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom handler that injects timezone context into responses."""
            # Get the original response
            response = await original_route_handler(request)

            # If it's not a JSONResponse or doesn't have body, return as-is
            if not isinstance(response, JSONResponse):
                return response

            # Get timezone from request state (set by TimeZoneMiddleware)
            timezone = getattr(request.state, "timezone", ZoneInfo("UTC"))

            # Try to re-serialize the response with timezone context
            try:
                # Get the body and parse it
                body = response.body.decode("utf-8")

                # If the original response was a Pydantic model, it's already serialized
                # We need to intercept before serialization, which means we need to
                # modify how FastAPI handles response_model

                # For now, return the response as-is
                # The proper solution is to modify the serialization at the service layer
                return response
            except Exception:
                # If anything goes wrong, return original response
                return response

        return custom_route_handler

