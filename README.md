# Book Borrowing Service

A service for managing book borrowings, returns, and reservations in a library management system.

## Features

- Book borrowing and returns management
- Reservation system with queuing
- Due date tracking and notifications
- Admin access to borrowing history
- Integration with authentication and book catalog services

## Tech Stack

- FastAPI (Python 3.11)
- MongoDB 7.0
- Redis 7
- Docker & Docker Compose

## Requirements

- Docker
- Docker Compose
- Python 3.11+ (for local development)

## Setup

1. Clone the repository:
    git clone https://github.com/Bhagavan-K/book-borrowing-service.git
    cd book-borrowing-service

2. Create .env file:
    MONGODB_URL=mongodb://mongodb:27018
    DATABASE_NAME=book_borrowing
    REDIS_URL=redis://redis:6380
    JWT_SECRET_KEY=yourprivatekey

3. Build and run with Docker:
    docker-compose up --build

4. Access the API documentation:
    http://localhost:8002/docs

## API Endpoints

### Default Health Check
- GET /health - Health Check

### Borrowing Operations
- POST /api/borrowings/borrow - Borrow a book
- POST /api/returns/return/{borrowing_id} - Return a book
- GET /api/borrowings/user/{user_id}/borrowings - Get user's borrowing history

### Reservation Operations
- POST /api/reservations/create - Create a reservation
- GET /api/reservations/queue/{book_id} - View reservation queue
- DELETE /api/reservations/{reservation_id} - Cancel reservation

### Admin Operations
- GET /api/borrowings/book/{book_id}/history - View book's borrowing history

## Running Tests

Install dependencies:
    pip install -r requirements.txt

Run tests:
    pytest tests/ -v

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URL | MongoDB connection URL | mongodb://mongodb:27018 |
| DATABASE_NAME | Database name | book_borrowing |
| REDIS_URL | Redis connection URL | redis://redis:6380 |
| JWT_SECRET_KEY | JWT secret key | yourprivatekey |

## Project Structure

book-borrowing-service/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies/
│   │   └── core/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── schemas/
│   └── main.py
├── tests/
├── docker-compose.yml
├── .env
└── Dockerfile

## Integration

This service integrates with:
- User Authentication Service for token validation and user management
- Book Catalog Service for book information and availability
- Redis for notification queuing and reservation management

## Core Functionality

### Borrowing Process
- Users can borrow available books
- 14-day default borrowing period
- Automatic due date tracking
- Overdue notifications

### Reservation System
- Queue-based reservation for borrowed books
- Automatic notification when book becomes available
- Position tracking in reservation queue
- Reservation expiry handling

### Admin Features
- View complete borrowing history for any book
- Access to user borrowing records
- System statistics and monitoring

## Testing

Test user credentials are provided for different roles:
- Regular User 1 (Predefined token)
- Regular User 2 (test_token_user2)
- Admin User (test_token_admin)

## Error Handling

The service includes comprehensive error handling for:
- Invalid tokens
- Unavailable books
- Unauthorized access
- Invalid operations
- Service integration failures

## Database Schema

### MongoDB Collections:
- books: Book status and metadata
- borrowings: Borrowing records and history
- reservations: Queue management and status

### Redis:
- Notification queues
- Reservation tracking
- Real-time status updates

## Running in Development

For local development:
1. Start MongoDB and Redis:
    docker-compose up mongodb redis

2. Start the FastAPI application:
    uvicorn app.main:app --reload --port 8002

## Monitoring

The service provides:
- Health check endpoint (/health)
- Basic metrics for monitoring
- Error logging and tracing
- Queue status monitoring

## Security

- JWT-based authentication
- Role-based access control
- Secure API endpoints
- Input validation and sanitization

## License

This project is licensed under the MIT License.