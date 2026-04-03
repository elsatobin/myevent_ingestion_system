# Event Ingestion System

## Overview

This project implements a production-style event ingestion pipeline
with:

-   Mock stream server (FastAPI)
-   Consumer + API service (FastAPI)
-   PostgreSQL persistence
-   Docker Compose setup

The system handles: - Duplicate events (idempotency) - Out-of-order
events - Fault tolerance and retries - Resume from checkpoint

------------------------------------------------------------------------

## Architecture

    Mock Stream Server ---> Consumer Service ---> PostgreSQL
                                   |
                                   v
                              REST API

------------------------------------------------------------------------

## Services

### 1. Mock Stream Server

-   Emits continuous JSON events over HTTP
-   Supports `?from_timepoint=` for resume

### 2. Consumer + API Service

-   Consumes stream continuously
-   Processes events safely
-   Stores raw + derived state
-   Exposes REST endpoints

------------------------------------------------------------------------

## Tech Stack

-   Python / FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Docker / Docker Compose

------------------------------------------------------------------------

## Running with Docker

### 1. Build and start

    docker-compose up --build

### 2. Services

-   API: http://localhost:8000
-   Stream: http://localhost:8001/stream

------------------------------------------------------------------------

## API Endpoints

### Get Events

    GET /events

### Get Entity

    GET /entities/{entity_id}

------------------------------------------------------------------------

## Environment Variables

    DATABASE_URL=postgresql://user:password@db:5432/events_db
    STREAM_URL=http://stream:8001/stream

------------------------------------------------------------------------

## Notes

See `NOTES.md` for design decisions and trade-offs.
