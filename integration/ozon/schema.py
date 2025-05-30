from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DiscountFailDetails(BaseModel):
    task_id: int
    error_for_user: str


class DiscountRequestSuccessResponse(BaseModel):
    fail_details: list[DiscountFailDetails] = []
    success_count: int
    fail_count: int
    status_code: Optional[int]


class DiscountRequestListResponse(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    end_at: Optional[datetime]
    edited_till: Optional[datetime]
    status: Optional[str]
    customer_name: Optional[str]
    sku: Optional[int]
    user_comment: Optional[str]
    seller_comment: Optional[str]
    requested_price: Optional[int]
    approved_price: Optional[int]
    original_price: Optional[int]
    discount: Optional[int]
    discount_percent: Optional[int]
    base_price: Optional[int]
    min_auto_price: Optional[int]
    prev_task_id: Optional[int]
    is_damaged: Optional[bool]
    moderated_at: Optional[datetime]
    approved_discount: Optional[int]
    approved_discount_percent: Optional[int]
    is_purchased: Optional[bool]
    is_auto_moderated: Optional[bool]
    offer_id: Optional[str]
    email: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    patronymic: Optional[str]
    approved_quantity_min: Optional[int]
    approved_quantity_max: Optional[int]
    requested_quantity_min: Optional[int]
    requested_quantity_max: Optional[int]
    requested_price_with_fee: Optional[int]
    approved_price_with_fee: Optional[int]
    approved_price_fee_percent: Optional[int]


class ProductPriceError(BaseModel):
    code: int
    message: str


class ProductPriceResult(BaseModel):
    product_id: int
    offer_id: str
    updated: bool
    errors: list[ProductPriceError] = []


class ProductImportPriceResponse(BaseModel):
    result: list[ProductPriceResult] = []


class ProductPriceErrorDetail(BaseModel):
    typeUrl: str
    value: str


class ProductImportPriceErrorResponse(BaseModel):
    code: int
    details: list[ProductPriceErrorDetail] = []
    message: str
