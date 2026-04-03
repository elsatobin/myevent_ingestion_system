# NOTES

## Decisions

**Idempotency via primary key**
Events are stored with `id` as the primary key. Any duplicate from the stream hits a no-op on the SELECT check before insert, so re-delivery is safe without needing upsert logic.

**Out-of-order handling**
Raw events are always persisted regardless of order. Entity state is only updated if the incoming `timepoint` is >= the entity's `last_timepoint`. This means we have a full audit log but the derived state reflects the latest known reality.

**Checkpoint by timepoint**
The checkpoint stores the last successfully processed `timepoint`, not event ID. On restart, the consumer passes `?from_timepoint=` to the stream server to resume. Combined with idempotency, any events re-delivered in the overlap window are safely ignored.

**Lazy engine init**
SQLAlchemy engine is initialized on first use rather than at module import time, ensuring the `DATABASE_URL` env var is available before the connection pool is created.

**Separate stream server**
`stream_server.py` runs as its own container. The consumer connects to it over HTTP using `httpx` async streaming. This mirrors a real production topology where the stream source is external.

## Trade-offs

- **No retry backoff on individual events** — a poison-pill event that consistently fails to parse or insert will be skipped with a warning log rather than blocking the pipeline. In production, a dead-letter queue would be appropriate.
- **Single checkpoint** — one global `timepoint` checkpoint works for a single-partition stream. A multi-partition stream would need per-partition checkpoints.
- **No auth** — credentials are hardcoded in docker-compose for local dev. In production these would come from a secrets manager.
- **Entity state is last-write-wins** — merging `updated` payloads with dict spread is simple but lossy if fields are deleted from the payload. A proper event-sourced projection would replay all events.

## What I'd do differently in production

- Replace the HTTP stream with Kafka or Kinesis for durability, backpressure, and multi-consumer support
- Add Alembic for schema migrations instead of `create_all`
- Structured logging (JSON) with correlation IDs per event
- Expose `/health` and `/metrics` endpoints
- Add integration tests for the idempotency and out-of-order paths
