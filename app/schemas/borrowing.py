from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class BorrowingCreate(BaseModel):
    user_id: int
    book_id: int

class BorrowingReturn(BaseModel):
    borrowing_id: str

class BorrowingResponse(BaseModel):
    id: str = Field(alias='_id')
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str
    renewals_count: int
    created_at: datetime
    updated_at: datetime

class BookHistoryResponse(BaseModel):
    book_id: int
    total_borrows: int
    current_status: str
    last_borrowed: Optional[datetime]
    last_returned: Optional[datetime]
    total_renewals: int

class ReservationCreate(BaseModel):
    user_id: int
    book_id: int

class ReservationResponse(BaseModel):
    id: str
    user_id: int
    book_id: int
    reservation_date: datetime
    status: str
    position: int
    created_at: datetime

class ReservationQueueResponse(BaseModel):
    book_id: int
    queue: List[ReservationResponse]