from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import datetime, timedelta
from ...schemas.borrowing import BorrowingCreate, BorrowingResponse, BookHistoryResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..dependencies.database import get_database
from ..dependencies.auth import get_current_user
from typing import List, Dict
from bson import ObjectId

router = APIRouter()

@router.post("/borrow", response_model=BorrowingResponse)
async def borrow_book(
    borrow: BorrowingCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Verify user
        if current_user["id"] != borrow.user_id:
            raise HTTPException(status_code=403, detail="Can only borrow books for yourself")
        
        # Check if book is available
        book = await db.books.find_one({"_id": borrow.book_id, "status": "AVAILABLE"})
        if not book:
            raise HTTPException(status_code=400, detail="Book not available")
        
        # Calculate due date (14 days from now)
        due_date = datetime.utcnow() + timedelta(days=14)
        current_time = datetime.utcnow()
        
        borrowing = {
            "user_id": borrow.user_id,
            "book_id": borrow.book_id,
            "borrow_date": current_time,
            "due_date": due_date,
            "status": "ACTIVE",
            "renewals_count": 0,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        result = await db.borrowings.insert_one(borrowing)
        
        # Update book status
        await db.books.update_one(
            {"_id": borrow.book_id},
            {"$set": {"status": "BORROWED"}}
        )
        
        borrowing["_id"] = str(result.inserted_id)
        return borrowing
        
    except Exception as e:
        # Rollback any changes if there's an error
        if 'result' in locals():
            await db.borrowings.delete_one({"_id": result.inserted_id})
            await db.books.update_one(
                {"_id": borrow.book_id},
                {"$set": {"status": "AVAILABLE"}}
            )
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user/{user_id}/borrowings", response_model=List[BorrowingResponse])
async def get_user_borrowings(
    user_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Verify current user or is admin
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Can only view your own borrowings")
    
    borrowings = []
    cursor = db.borrowings.find({"user_id": user_id})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        borrowings.append(doc)
    return borrowings

@router.get("/book/{book_id}/history", response_model=List[BorrowingResponse])
async def get_book_history(
    book_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Verify admin access
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only administrators can view book borrowing history"
        )
    
    # Get all borrowing records for this book
    borrowings = []
    cursor = db.borrowings.find({"book_id": book_id}).sort("created_at", -1)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        borrowings.append(doc)
    
    if not borrowings:
        # Check if book exists
        book = await db.books.find_one({"_id": book_id})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
    
    return borrowings