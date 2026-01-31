# Corplang Project Configuration - PostgreSQL Example
# This demonstrates how to configure PostgreSQL for migrations

name: "postgres_example"
description: "Example project using PostgreSQL with migrations"
language_version: "0.1.0"

# Module search paths
module_paths:
  - ./lib
  - ./src
  - ./modules

# Database Configuration
database:
  # Driver: sqlite, postgresql (or postgres alias)
  driver: "postgresql"
  # DSN: database connection string
  # Format: postgresql://username:password@hostname:port/database
  # Example with default PostgreSQL on localhost:
  dsn: "postgresql://user:password@localhost:5432/myapp"
  
  # For development with default PostgreSQL:
  # dsn: "postgresql://postgres@localhost:5432/myapp"
  
  # For Docker PostgreSQL:
  # dsn: "postgresql://postgres:password@postgres:5432/myapp"
