from typing import Any
from pydantic import BaseModel, Field
from common.exceptions.common import GeneralError


class ErrorDetail(BaseModel):
    """Defines the detailed structure of a single API error."""

    loc: str = Field(..., description="Location where the error occurred.")
    msg: str = Field(..., description="A human-readable message explaining the error.")
    type: str = Field(..., description="A unique, machine-readable code for the error type.")


class ErrorResponse(BaseModel):
    """Defines the standard model for all error responses."""

    detail: list[ErrorDetail]


def generate_responses(*exceptions: type[GeneralError]) -> dict[int | str, dict[str, Any]]:
    """
    Generates an OpenAPI 'responses' dictionary from exception classes.

    This function creates response metadata for API endpoints, including a formal
    schema and specific examples for different error conditions. It correctly
    groups multiple exceptions under a single HTTP status code.

    Args:
        *exceptions: A list of exception classes that inherit from GeneralError.

    Returns:
        A dictionary formatted for the 'responses' parameter of a FastAPI decorator.
    """
    responses: dict[int | str, Any] = {}
    grouped_by_status: dict[int, list[type[GeneralError]]] = {}

    for exc_class in exceptions:
        grouped_by_status.setdefault(exc_class.status_code, []).append(exc_class)

    for status_code, exc_list in grouped_by_status.items():
        examples = {
            exc_class.__name__: {
                "summary": exc_class.message,
                "value": {
                    "detail": [
                        {
                            "loc": exc_class.loc,
                            "msg": exc_class.message,
                            "type": exc_class.__name__,
                        }
                    ]
                },
            }
            for exc_class in exc_list
        }

        responses[status_code] = {
            "model": ErrorResponse,
            "content": {"application/json": {"examples": examples}},
        }
    return responses
