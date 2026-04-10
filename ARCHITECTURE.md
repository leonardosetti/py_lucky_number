# Lucky Number - Architecture Documentation

## Overview

Lucky Number is a FastAPI-based web application that generates lottery number combinations that have never been drawn before, using data from the Brazilian Caixa Econômica Federal lottery API.

## System Architecture

### Current State (Monolithic)



## Components

### 1. API Layer ()
- **routes.py**: HTTP endpoints and request handling
- **dependencies.py**: FastAPI dependency injection

### 2. Service Layer ()
- **caixa_api.py**: External API integration with retry logic
- **cache.py**: In-memory caching for lottery results
- **gerador.py**: Business logic for generating unique combinations

### 3. Configuration ()
- Lottery game rules and constraints
- API endpoints configuration
- Validation constants

## Technology Stack

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic 2.0+
- **Testing**: pytest with asyncio support
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Deployment Strategies

### Development


### Production


## Future Architecture

See [MICROSERVICES_PLAN.md](MICROSERVICES_PLAN.md) for migration strategy.
