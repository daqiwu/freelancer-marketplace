"""
Security Issue Classification API Routes
Provides endpoints for AI-powered security issue classification and management
"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_db
from app.models.models import (
    SecurityIssue,
    SecurityIssueStatus,
    SecurityIssueType,
    SecuritySeverity,
    User,
)
from app.routes.auth import get_current_user
from app.services.security_classifier_service import SecurityClassifierService


# Pydantic models for request/response
class SecurityIssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    affected_component: Optional[str] = Field(None, max_length=500)
    assigned_to: Optional[int] = None


class SecurityIssueResponse(BaseModel):
    id: int
    title: str
    description: str
    issue_type: str
    severity: str
    confidence_score: float
    affected_component: Optional[str]
    vulnerability_id: Optional[str]
    detection_method: Optional[str]
    tags: List[str]
    remediation_suggestion: Optional[str]
    remediation_priority: Optional[int]
    estimated_effort: Optional[str]
    status: str
    reported_by: int
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class SecurityIssueUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None


class BatchClassifyRequest(BaseModel):
    issues: List[SecurityIssueCreate]


class SecurityStatistics(BaseModel):
    total: int
    by_type: dict
    by_severity: dict
    by_status: dict
    avg_confidence: float


# Initialize router
security_router = APIRouter(prefix="/api/security", tags=["Security Classification"])

# Initialize classifier service
classifier_service = SecurityClassifierService()


@security_router.post(
    "/issues", response_model=SecurityIssueResponse, status_code=status.HTTP_201_CREATED
)
async def create_security_issue(
    issue_data: SecurityIssueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new security issue with AI classification

    This endpoint:
    1. Receives security issue details
    2. Uses AI to classify the issue type (SCA/SAST/DAST)
    3. Determines severity and provides remediation suggestions
    4. Stores the classified issue in the database
    """
    try:
        # Use AI to classify the issue
        classification = classifier_service.classify_issue(
            title=issue_data.title,
            description=issue_data.description,
            affected_component=issue_data.affected_component or "",
        )

        # Create security issue
        security_issue = SecurityIssue(
            title=issue_data.title,
            description=issue_data.description,
            affected_component=issue_data.affected_component,
            issue_type=SecurityIssueType[classification["issue_type"]],
            severity=SecuritySeverity[classification["severity"]],
            confidence_score=classification["confidence_score"],
            vulnerability_id=classification["vulnerability_id"],
            detection_method=classification["detection_method"],
            tags=classification["tags"],
            remediation_suggestion=classification["remediation_suggestion"],
            remediation_priority=classification["remediation_priority"],
            estimated_effort=classification["estimated_effort"],
            reported_by=current_user.id,
            assigned_to=issue_data.assigned_to,
            status=SecurityIssueStatus.OPEN,
        )

        db.add(security_issue)
        await db.commit()
        await db.refresh(security_issue)

        # Parse tags for response
        response_data = {
            **security_issue.__dict__,
            "issue_type": security_issue.issue_type.value,
            "severity": security_issue.severity.value,
            "status": security_issue.status.value,
            "tags": json.loads(security_issue.tags) if security_issue.tags else [],
        }

        return SecurityIssueResponse(**response_data)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create security issue: {str(e)}",
        )


@security_router.get("/issues", response_model=List[SecurityIssueResponse])
async def get_security_issues(
    issue_type: Optional[str] = None,
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get security issues with optional filters

    Filters:
    - issue_type: SCA, SAST, DAST, UNKNOWN
    - severity: CRITICAL, HIGH, MEDIUM, LOW, INFO
    - status: OPEN, IN_PROGRESS, RESOLVED, DISMISSED
    """
    try:
        query = select(SecurityIssue)

        # Apply filters
        conditions = []
        if issue_type:
            conditions.append(SecurityIssue.issue_type == SecurityIssueType[issue_type])
        if severity:
            conditions.append(SecurityIssue.severity == SecuritySeverity[severity])
        if status_filter:
            conditions.append(
                SecurityIssue.status == SecurityIssueStatus[status_filter]
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = (
            query.offset(skip).limit(limit).order_by(SecurityIssue.created_at.desc())
        )

        result = await db.execute(query)
        issues = result.scalars().all()

        # Format response
        response = []
        for issue in issues:
            response.append(
                SecurityIssueResponse(
                    **{
                        **issue.__dict__,
                        "issue_type": issue.issue_type.value,
                        "severity": issue.severity.value,
                        "status": issue.status.value,
                        "tags": json.loads(issue.tags) if issue.tags else [],
                    }
                )
            )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve security issues: {str(e)}",
        )


@security_router.get("/issues/{issue_id}", response_model=SecurityIssueResponse)
async def get_security_issue(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific security issue by ID"""
    try:
        result = await db.execute(
            select(SecurityIssue).where(SecurityIssue.id == issue_id)
        )
        issue = result.scalar_one_or_none()

        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Security issue not found"
            )

        return SecurityIssueResponse(
            **{
                **issue.__dict__,
                "issue_type": issue.issue_type.value,
                "severity": issue.severity.value,
                "status": issue.status.value,
                "tags": json.loads(issue.tags) if issue.tags else [],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve security issue: {str(e)}",
        )


@security_router.patch("/issues/{issue_id}", response_model=SecurityIssueResponse)
async def update_security_issue(
    issue_id: int,
    update_data: SecurityIssueUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a security issue (status, assignee)"""
    try:
        result = await db.execute(
            select(SecurityIssue).where(SecurityIssue.id == issue_id)
        )
        issue = result.scalar_one_or_none()

        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Security issue not found"
            )

        # Update fields
        if update_data.status:
            issue.status = SecurityIssueStatus[update_data.status]
            if update_data.status == "RESOLVED":
                issue.resolved_at = datetime.utcnow()

        if update_data.assigned_to is not None:
            issue.assigned_to = update_data.assigned_to

        issue.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(issue)

        return SecurityIssueResponse(
            **{
                **issue.__dict__,
                "issue_type": issue.issue_type.value,
                "severity": issue.severity.value,
                "status": issue.status.value,
                "tags": json.loads(issue.tags) if issue.tags else [],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update security issue: {str(e)}",
        )


@security_router.post("/batch-classify", response_model=List[dict])
async def batch_classify_issues(
    batch_request: BatchClassifyRequest, current_user: User = Depends(get_current_user)
):
    """
    Classify multiple security issues in batch without saving to database

    Useful for:
    - Testing the classifier
    - Previewing classifications before saving
    - Batch processing external security scan results
    """
    try:
        issues = [
            {
                "title": issue.title,
                "description": issue.description,
                "component": issue.affected_component or "",
            }
            for issue in batch_request.issues
        ]

        results = classifier_service.batch_classify(issues)

        # Convert Decimal to float for JSON serialization
        for result in results:
            if "confidence_score" in result:
                result["confidence_score"] = float(result["confidence_score"])
            if "tags" in result:
                result["tags"] = json.loads(result["tags"])

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify issues: {str(e)}",
        )


@security_router.get("/statistics", response_model=SecurityStatistics)
async def get_security_statistics(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about security issues

    Returns:
    - Total count
    - Distribution by type (SCA/SAST/DAST)
    - Distribution by severity
    - Distribution by status
    - Average confidence score
    """
    try:
        # Get all issues
        result = await db.execute(select(SecurityIssue))
        issues = result.scalars().all()

        total = len(issues)

        if total == 0:
            return SecurityStatistics(
                total=0, by_type={}, by_severity={}, by_status={}, avg_confidence=0.0
            )

        # Calculate distributions
        by_type = {}
        by_severity = {}
        by_status = {}
        total_confidence = 0.0

        for issue in issues:
            # Type distribution
            type_key = issue.issue_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Severity distribution
            severity_key = issue.severity.value
            by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

            # Status distribution
            status_key = issue.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            # Confidence
            total_confidence += float(issue.confidence_score)

        avg_confidence = total_confidence / total

        return SecurityStatistics(
            total=total,
            by_type=by_type,
            by_severity=by_severity,
            by_status=by_status,
            avg_confidence=round(avg_confidence, 2),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )


@security_router.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_security_issue(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a security issue (admin only)"""
    try:
        # Check if user is admin
        if current_user.role.role_name not in ["admin", "provider"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete security issues",
            )

        result = await db.execute(
            select(SecurityIssue).where(SecurityIssue.id == issue_id)
        )
        issue = result.scalar_one_or_none()

        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Security issue not found"
            )

        await db.delete(issue)
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete security issue: {str(e)}",
        )
