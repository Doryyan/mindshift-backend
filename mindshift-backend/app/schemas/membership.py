from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MembershipUpgradeRequest(BaseModel):
    plan_id: int


class MembershipVerifyReceiptRequest(BaseModel):
    receipt_data: str
    transaction_id: str
    product_id: str


class MembershipStatusResponse(BaseModel):
    has_membership: bool
    plan_name: str
    status: str
    starts_at: str | None = None
    expires_at: str | None = None
    auto_renew: bool = False


class MembershipRestoreResponse(BaseModel):
    found: bool
    plan_name: str
    level: str
    status: str
    expires_at: str | None = None
    auto_renew: bool


class MembershipCancelResponse(BaseModel):
    success: bool
    message: str
    cancelled_at: str


class MembershipUpgradeResponse(BaseModel):
    success: bool
    membership_id: str
    plan_name: str
    status: str
    starts_at: str
    expires_at: str | None = None
