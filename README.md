#  Doing CRUD with FastAPI & MongoDB

This is a FastAPI project that demonstrates simple CRUD operations using MongoDB with Beanie as the ODM. The project is divided into two services: `admin` for user management and `product` for managing product information. It supports user authentication through JWT tokens and ensures secure access to product-related APIs.

## Features

### Admin Service
- **POST /admin/signup**: Register new users with an email and password.
- **POST /admin/login**: Authenticate users with their credentials, and issue a JWT token upon successful login.
- **GET /admin/healthz**: Health check endpoint that verifies MongoDB connectivity.

### Product Service
Every single Product API is protected & requires JWT token
- **GET /products**: Retrieve all available products.
- **GET /products/filter**: Filter products by category, brand, and limit the results.
- **GET /products/{id}**: Fetch a specific product by its ID.
- **DELETE /products/{id}**: Delete a specific product by its ID.
- **PUT /products/{id}**: Update a specific product by its ID.
- **POST /products**: Create new products.
- **GET /products/healthz**: Health check endpoint that verifies MongoDB connectivity.

## Tech Stack
- **FastAPI**: For building the APIs.
- **MongoDB**: For data storage.
- **Beanie ODM**: For managing MongoDB interactions.
- **JWT**: For authentication and secure access.
- **Docker**: To containerize the application.

## Project Structure
```
project/
├── admin/
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── admin.py
│   ├── schema/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── .dockerignore       
│   ├── Dockerfile         
│   ├── logger.py
│   ├── main.py
│   ├── oauth.py
│   ├── requirements.txt
│   └── session.py
├── product/
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── routers/
│   │   └── product.py
│   ├── schema/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── .dockerignore       
│   ├── Dockerfile          
│   ├── logger.py
│   ├── main.py
│   ├── oauth.py
│   ├── requirements.txt
│   └── session.py
├── .gitignore              
└── README.md

```

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/musatee/doing-crud-with-fastapi.git
   cd doing-crud-with-fastapi
   ```
2. **Build Docker Image:**
   ```bash
   cd admin
   docker build -t admin . 
   cd product
   docker build -t product .
   ``` 
3. **Create a custom Docker Network of type Bridge:**
    ```bash
    docker network create ecom --driver bridge
    ```
4. **Run the services:**
   ```bash
   docker run -itd --name admin \
   -p 8080:8000 --network ecom \
   -e db_username=<username> \
   -e db_password=<password> \
   -e log_path="/app/log" \
   -e db_host=<mongodb_host> admin 

   docker run -itd --name product \
   -p 9090:8000 --network ecom \
   -e db_username=<username> \
   -e db_password=<password> \
   -e db_host=<mongodb_host> \
   -e token_url="http://127.0.0.1:8080/admin/login" \
   -e log_path="/app/log" product
   ```
   >NOTE: the mongodb container must be running in the same docker network with name "mongo"