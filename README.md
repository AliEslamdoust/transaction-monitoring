# Transaction Monitoring System

A real-time transaction monitoring system built with Django, Django REST Framework, Celery, and Django Channels. This application provides high-performance transaction processing with real-time WebSocket updates and efficient background task processing.

## Features

- **Real-time Transaction Updates**: WebSocket support for live transaction notifications
- **High-Performance Processing**: Redis-backed queue system for handling high-volume transactions
- **Bulk Processing**: Periodic batch insertion of transactions using Celery Beat
- **RESTful API**: Complete API for transaction management
- **Transaction Analytics**: Average transaction amount calculations with date range filtering
- **PostgreSQL Database**: Reliable data persistence
- **Admin Monitoring**: WebSocket-based admin dashboard for real-time transaction monitoring

## Technology Stack

- **Backend Framework**: Django 5.2.8
- **API Framework**: Django REST Framework 3.15.2
- **Database**: PostgreSQL (psycopg2-binary 2.9.10)
- **Cache & Message Broker**: Redis 5.2.1
- **Async Processing**: Celery 5.4.0
- **WebSockets**: Django Channels 4.2.0 with channels-redis 4.2.1
- **ASGI Server**: Daphne 4.1.2
- **Static Files**: WhiteNoise 6.8.2

## Prerequisites

Before running this application, ensure you have the following installed:

- Python 3.10 or higher
- PostgreSQL
- Redis Server

## Installation

1. **Clone the repository**
   ```bash
   cd d:\py-django-rest\8
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # On Windows
   # source env/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL Database**
   
   Create a PostgreSQL database with the following credentials (or update `settings.py`):
   - Database Name: `transactions_database`
   - User: `admin`
   - Password: `12345678`
   - Host: `localhost`
   - Port: Default (5432)

   Connect to PostgreSQL as the superuser:
   ```bash
   psql -U postgres # On Windows
   # sudo -u postgres psql # On Linux/Mac
   ```

   Create a new database and user:
   ```sql
   CREATE DATABASE transactions_database;
   CREATE USER admin WITH PASSWORD '12345678';
   GRANT ALL PRIVILEGES ON DATABASE transactions_database TO admin;
   ```

   Switch the database context using the \c meta-command:
   ```sql
   \c transactions_database
   ```

   Grant CREATE permission to user:
   ```sql
   GRANT CREATE ON SCHEMA public TO admin;
   ```

   EXit the terminal:
   ```sql
   \q
   ```

5. **Start Redis Server**
   
   Ensure Redis is running on `localhost:6379`
   ```bash
   redis-server
   ```

6. **Run Database Migrations**
   ```bash
   cd transaction_monitoring
   python manage.py migrate
   ```

7. **Create a Superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

## Running the Application

This application requires three separate processes to run simultaneously:

### 1. ASGI Server (Daphne)

Run the Daphne server for Django Channels WebSocket support:
```bash
cd transaction_monitoring
daphne -p 8000 transaction_monitoring.asgi:application
```

### 2. Celery Worker

Start the Celery worker for background task processing:
```bash
cd transaction_monitoring
celery -A transaction_monitoring worker -l info
```

### 3. Celery Beat

Start the Celery Beat scheduler for periodic tasks (flushes transactions from Redis to PostgreSQL every 5 seconds):
```bash
cd transaction_monitoring
celery -A transaction_monitoring beat -l info
```

## API Endpoints

### Add Transaction
- **URL**: `/api/add-transaction/`
- **Method**: `POST`
- **Description**: Adds a transaction to the Redis queue and sends real-time update via WebSocket
- **Request Body**:
  ```json
  {
    "transaction_id": "TRX123456",
    "user": 1,
    "amount": 1000,
    "status": "PENDING"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Transaction detail was obtained successfully."
  }
  ```

### Get Transaction
- **URL**: `/api/transactions/<id>/`
- **Method**: `GET`
- **Description**: Retrieves a specific transaction by ID

### Get Transaction Averages
- **URL**: `/api/transactions/average/?from=YYYY-MM-DD&to=YYYY-MM-DD`
- **Method**: `GET`
- **Description**: Calculates average transaction amounts grouped by day within a date range
- **Query Parameters**:
  - `from`: Start date (optional, defaults to earliest transaction date)
  - `to`: End date (optional, defaults to latest transaction date)

### Delete All Transactions (Testing)
- **URL**: `/api/delete-transactions/`
- **Method**: `DELETE`
- **Description**: Deletes all transactions (for testing purposes only)

## WebSocket Connection

### Admin Transaction Updates
- **URL**: `ws://localhost:8000/ws/admin/transactions/`
- **Description**: Connect to receive real-time transaction updates
- **Message Format**:
  ```json
  {
    "transaction_id": "TRX123456",
    "user": 1,
    "amount": 1000,
    "status": "PENDING"
  }
  ```

## Architecture

### Transaction Flow

1. **Transaction Creation**: Client sends POST request to `/api/add-transaction/`
2. **Redis Queue**: Transaction data is pushed to Redis list (`transactions_list`)
3. **WebSocket Broadcast**: Real-time update sent to all connected admin clients
4. **Periodic Flush**: Celery Beat triggers `flush_transactions` task every 5 seconds
5. **Bulk Insert**: Transactions are bulk-inserted from Redis to PostgreSQL
6. **Queue Cleanup**: Successfully inserted transactions are removed from Redis

### Transaction Model

```python
class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(validators=[MinValueValidator(0)])
```

**Payment Statuses**:
- `PENDING`: Transaction is pending
- `SUCCESS`: Transaction completed successfully
- `FAILED`: Transaction failed

## Configuration

Key settings are located in `transaction_monitoring/settings.py`:

- **Celery Configuration**: Lines 150-161
- **Redis Cache Configuration**: Lines 163-171
- **Channel Layers**: Lines 78-85
- **Database Configuration**: Lines 90-98

## Testing

The project includes high-load transaction tests. To run tests:

```bash
cd transaction_monitoring
python manage.py test
```

### High Load Test

The test suite includes `HighLoadTransactionTest` which:
- Creates 50 distinct users
- Simulates each user sending 50 concurrent requests
- Tests system performance under high load (2,500 total concurrent requests)

## Celery Task Information

To view registered Celery tasks:
```bash
celery -A transaction_monitoring inspect registered
```

## Production Considerations

> [!WARNING]
> **Security**: The current `SECRET_KEY` in `settings.py` is insecure and should be changed for production use.

> [!IMPORTANT]
> **Debug Mode**: Set `DEBUG = False` in production and configure `ALLOWED_HOSTS` appropriately.

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use environment variables for sensitive credentials
- [ ] Set up proper PostgreSQL user permissions
- [ ] Configure Redis persistence
- [ ] Use a process manager (e.g., Supervisor, systemd) for Celery workers
- [ ] Set up proper logging
- [ ] Configure HTTPS with a reverse proxy (e.g., Nginx)
- [ ] Implement rate limiting for API endpoints

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running: `redis-cli ping` (should return `PONG`)
   - Check Redis is listening on port 6379

2. **PostgreSQL Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `settings.py`
   - Ensure database exists and user has proper permissions

3. **WebSocket Connection Failed**
   - Confirm Daphne server is running
   - Check that `channels` and `channels-redis` are installed
   - Verify Redis is accessible

4. **Celery Tasks Not Running**
   - Ensure both Celery worker and beat are running
   - Check Redis connection
   - Verify task registration: `celery -A transaction_monitoring inspect registered`

## Project Structure

```
transaction_monitoring/
├── manage.py
├── transaction_monitoring/
│   ├── __init__.py
│   ├── asgi.py              # ASGI configuration
│   ├── celery.py            # Celery configuration
│   ├── consumers.py         # WebSocket consumers
│   ├── routing.py           # WebSocket URL routing
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
└── transactions/
    ├── __init__.py
    ├── admin.py             # Django admin configuration
    ├── apps.py              # App configuration
    ├── models.py            # Transaction model
    ├── serializers.py       # DRF serializers
    ├── tasks.py             # Celery tasks
    ├── tests.py             # Test suite
    ├── urls.py              # App URL configuration
    └── views.py             # API views
```

## License

This project is for educational and development purposes.

## Contributing

This is a personal project. For questions or suggestions, please contact the repository owner.

---

**Author**: Ali Eslamdoust  
**Last Updated**: December 2025
