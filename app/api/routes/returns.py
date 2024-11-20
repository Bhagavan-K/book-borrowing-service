from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from ...schemas.borrowing import BorrowingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..dependencies.database import get_database
from bson import ObjectId

router = APIRouter()

@router.post("/return/{borrowing_id}", response_model=BorrowingResponse)
async def return_book(
    borrowing_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        borrowing = await db.borrowings.find_one({"_id": ObjectId(borrowing_id)})
        if not borrowing:
            raise HTTPException(status_code=404, detail="Borrowing record not found")
            
        if borrowing["status"] != "ACTIVE":
            raise HTTPException(status_code=400, detail="Book already returned")
        
        # Update borrowing record
        update_result = await db.borrowings.update_one(
            {"_id": ObjectId(borrowing_id)},
            {
                "$set": {
                    "status": "RETURNED",
                    "return_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update book status
        await db.books.update_one(
            {"_id": borrowing["book_id"]},
            {"$set": {"status": "AVAILABLE"}}
        )
        
        # Get updated borrowing record
        updated_borrowing = await db.borrowings.find_one({"_id": ObjectId(borrowing_id)})
        updated_borrowing["_id"] = str(updated_borrowing["_id"])
        return updated_borrowing
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))