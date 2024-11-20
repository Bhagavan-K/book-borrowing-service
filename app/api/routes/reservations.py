from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.services.notification_service import NotificationService
from ...schemas.borrowing import ReservationCreate, ReservationResponse, ReservationQueueResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..dependencies.database import get_database
from ..dependencies.redis import get_redis
from ..dependencies.auth import get_current_user
from redis.asyncio import Redis
from typing import Dict
from bson import ObjectId
import json

router = APIRouter()

@router.post("/create", response_model=ReservationResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis: Redis = Depends(get_redis)
):
    # Verify user
    if current_user["id"] != reservation.user_id:
        raise HTTPException(status_code=403, detail="Can only create reservations for yourself")
    
    # Check if book exists and is borrowed
    book = await db.books.find_one({"_id": reservation.book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book["status"] != "BORROWED":
        raise HTTPException(status_code=400, detail="Can only reserve borrowed books")
    
    # Check if user already has a reservation for this book
    existing = await db.reservations.find_one({
        "user_id": reservation.user_id,
        "book_id": reservation.book_id,
        "status": "WAITING"
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already reserved")
    
    # Get queue position
    queue_len = await redis.llen(f"book_queue:{reservation.book_id}")
    
    reservation_doc = {
        "user_id": reservation.user_id,
        "book_id": reservation.book_id,
        "reservation_date": datetime.utcnow(),
        "status": "WAITING",
        "position": queue_len + 1,
        "created_at": datetime.utcnow()
    }
    
    result = await db.reservations.insert_one(reservation_doc)
    reservation_doc["id"] = str(result.inserted_id)
    
    # Add to Redis queue
    await redis.rpush(
        f"book_queue:{reservation.book_id}",
        json.dumps({"reservation_id": str(result.inserted_id), "user_id": reservation.user_id})
    )
    
    notification_service = NotificationService(redis)
    await notification_service.send_reservation_notification(
        reservation.user_id,
        reservation.book_id,
        queue_len + 1
    )

    return reservation_doc


@router.get("/queue/{book_id}", response_model=ReservationQueueResponse)
async def get_reservation_queue(
    book_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis: Redis = Depends(get_redis)
):
    # Get queue from Redis
    queue = []
    raw_queue = await redis.lrange(f"book_queue:{book_id}", 0, -1)
    
    for item in raw_queue:
        data = json.loads(item)
        reservation = await db.reservations.find_one({"_id": ObjectId(data["reservation_id"])})
        if reservation:
            reservation["id"] = str(reservation["_id"])
            queue.append(reservation)
    
    return {"book_id": book_id, "queue": queue}

@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis: Redis = Depends(get_redis)
):
    # Verify user owns the reservation or is admin
    reservation = await db.reservations.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if current_user["id"] != reservation["user_id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Can only cancel your own reservations")
    
    reservation = await db.reservations.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Remove from Redis queue
    queue_key = f"book_queue:{reservation['book_id']}"
    queue = await redis.lrange(queue_key, 0, -1)
    
    for idx, item in enumerate(queue):
        data = json.loads(item)
        if data["reservation_id"] == reservation_id:
            await redis.lrem(queue_key, 1, item)
            break
    
    # Update status in MongoDB
    await db.reservations.update_one(
        {"_id": ObjectId(reservation_id)},
        {"$set": {"status": "CANCELLED"}}
    )
    
    return {"message": "Reservation cancelled successfully"}