# Thrifty – Used-Items Marketplace API

Thrifty is a RESTful backend API for a used-items marketplace where users can
sell, buy, auction, or donate items through a single platform.

The project was developed using Django REST Framework and Python as the backend section of a final-year university project 

## Features

- User registration and JWT authentication
- User profiles and seller ratings
- Create, update, and manage item listings
- Multiple listing choices (fixed price, auction, donation)
- Item categories
- Favorites and personalized recommendations based on favorite categories and purchase history
- Purchase and transaction management
- Wallet-based balance system
- Real-time buyer/seller communication
- User reporting system
- Admin management and monitoring
- Multiple images per item
- Auction expiration and winner processing

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- SimpleJWT
- Stream Chat
- Redis
- Cloudinary
- Supabsase
- Azure

## Architecture

The project follows a RESTful API architecture using Django REST Framework.

## Authentication

The API uses JWT authentication through SimpleJWT.

Authenticated requests require an access token:

Authorization: Bearer <access_token>

## API Structure

The API provides endpoints for:

- Authentication
- Users
- Items
- Categories
- Bids
- Purchases
- Wallet
- Favorite Categories
- Recommendations
- Reports
- Item images
- Chat

## Deployment

The backend has been deployed using cloud platforms including Azure Cloudinary and Supabase.

## Project Structure

thrifty_api/
├── categories/        # Item categories and category hierarchy
├── chat/              # Buyer-item-seller chat integration
├── favorites/         # User favorite categories
├── items/             # Items, listings, bidding and item management
├── ratings/           # Seller ratings
├── reports/           # User reports and admin management
├── users/             # User accounts, authentication and profiles
├── wallet/            # Wallet balances and transactions
│
├── thrifty_api/       # Main Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
│
├── .github/
│   └── workflows/     # CI/CD configuration
│
├── manage.py
├── requirements.txt
├── build.sh
└── runtime.txt
