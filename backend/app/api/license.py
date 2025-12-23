# Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
# PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.

"""
License and Code Tracking API Endpoints

This module provides endpoints for:
- License verification
- Deployment tracking
- Usage analytics for compliance

WARNING: These endpoints are protected and monitored.
Unauthorized access attempts will be logged and reported.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user_id
from app.utils.code_tracking import (
    get_fingerprint,
    get_tracker,
    get_tracking_headers,
    verify_deployment,
)

router = APIRouter(prefix="/license", tags=["License & Tracking"])


@router.get("/info")
async def get_license_info(request: Request):
    """
    Get license and copyright information.

    Returns:
        License information including build fingerprint and copyright notice.
    """
    fingerprint = get_fingerprint()
    tracker = get_tracker()

    # Log access
    tracker.log_access(
        endpoint="/license/info",
        method="GET",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    response = JSONResponse(
        content={
            "product": "Legal Evidence Hub",
            "copyright": "Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.",
            "license_type": "Proprietary Software License",
            "restrictions": [
                "Unauthorized copying prohibited",
                "Unauthorized distribution prohibited",
                "Unauthorized modification prohibited",
                "Reverse engineering prohibited",
            ],
            "build_info": {
                "fingerprint": fingerprint.get_build_fingerprint(),
                "environment": fingerprint.get_environment_fingerprint()[:16] + "...",
            },
            "legal_notice": (
                "This software is protected by copyright law and international treaties. "
                "Unauthorized reproduction or distribution may result in severe civil and "
                "criminal penalties."
            ),
            "contact": {
                "licensing": "legal@legalevidence.hub",
                "security": "security@legalevidence.hub",
            },
        }
    )

    # Add tracking headers
    for key, value in get_tracking_headers().items():
        response.headers[key] = value

    return response


@router.get("/verify")
async def verify_license(
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """
    Verify deployment authorization (requires authentication).

    Returns:
        Deployment verification status and tracking token.
    """
    tracker = get_tracker()

    tracker.log_access(
        endpoint="/license/verify",
        method="GET",
        user_id=user_id,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    verification = verify_deployment()

    response = JSONResponse(
        content={
            "authorized": True,
            "verification": verification,
            "message": "Deployment verified successfully",
        }
    )

    for key, value in get_tracking_headers().items():
        response.headers[key] = value

    return response


@router.get("/tracking/summary")
async def get_tracking_summary(
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get usage tracking summary (requires authentication).

    Returns:
        Summary of API usage for compliance monitoring.
    """
    tracker = get_tracker()

    tracker.log_access(
        endpoint="/license/tracking/summary",
        method="GET",
        user_id=user_id,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    summary = tracker.get_usage_summary()

    response = JSONResponse(
        content={
            "usage_summary": summary,
            "tracking_enabled": True,
            "compliance_status": "active",
        }
    )

    for key, value in get_tracking_headers().items():
        response.headers[key] = value

    return response


@router.get("/fingerprint")
async def get_deployment_fingerprint(request: Request):
    """
    Get current deployment fingerprint.

    Returns:
        Build and environment fingerprints for tracking.
    """
    fingerprint = get_fingerprint()
    tracker = get_tracker()

    tracker.log_access(
        endpoint="/license/fingerprint",
        method="GET",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    response = JSONResponse(
        content={
            "build_fingerprint": fingerprint.get_build_fingerprint(),
            "environment_fingerprint": fingerprint.get_environment_fingerprint(),
            "instance_fingerprint": fingerprint.get_instance_fingerprint(),
            "copyright": "Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.",
        }
    )

    for key, value in get_tracking_headers().items():
        response.headers[key] = value

    return response
