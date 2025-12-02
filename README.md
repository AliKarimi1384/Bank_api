### Bank API task

## Installation & Setup

## 1. Install Prerequisites
Ensure you have Python 3.10+ and PostgreSQL installed. Then, install the dependencies:
pip install -r requirements.txt

## 2. Configure Database
Create an empty database named bank_db in PostgreSQL.

Create a .env file in the root directory and add the following configuration:

DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/bank_db
API_KEY=bank-secret-key

## 3. Initialize Database & Seed Data
Run the following commands to create the tables and generate 100,000 test transactions:

python -m alembic upgrade head
python seeder.py

## 4. Run the Server
Start the application using Uvicorn:

uvicorn app.main:app --reload