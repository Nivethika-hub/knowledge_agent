# Phase 8.2–8.6 Swagger Testing Guide

## 1. Start the API

From the `backend` directory:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and confirm that
the **Automation** tag contains `POST /automation/run`.

## 2. Establish the in-memory baseline

In Swagger, expand `POST /automation/run`, select **Try it out**, then
**Execute**. The first call after the FastAPI process starts establishes the
current maximum primary key for Slack, Jira, GitHub, and Notion. It should
return HTTP 200:

```json
{
  "events_detected": 0,
  "updated_features": [],
  "vectors_updated": 0,
  "notifications_created": 0,
  "status": "Automation completed successfully"
}
```

This first-run behaviour prevents historical records from being reprocessed.

## 3. Create one source event

Insert a new record through the enterprise simulator or a trusted PostgreSQL
client. The currently exposed Slack, Jira, GitHub, and Notion endpoints are
read-only, so Swagger cannot create this source record itself.

For a local test, insert a Slack record associated with an existing feature:

```sql
INSERT INTO slack_messages
    (project_id, member_id, channel_name, message, message_time, related_feature)
VALUES
    (1, 1, 'backend', 'PostgreSQL schema decision was reviewed.', NOW(), 'Database Design');
```

Use valid `project_id` and `member_id` values from your local database. Keep
the FastAPI process running between steps 2 and 4; the monitor state is
intentionally in memory.

## 4. Run the automation

Execute `POST /automation/run` again in Swagger. The response should resemble:

```json
{
  "events_detected": 1,
  "updated_features": ["Database Design"],
  "vectors_updated": 1,
  "notifications_created": 1,
  "status": "Automation completed successfully"
}
```

The request performs this sequence synchronously:

1. Detect the new source row by its primary key.
2. Regenerate the affected Knowledge Node.
3. Upsert its existing ChromaDB document and embedding.
4. Insert an unread `notifications` row.

## 5. Verify results

Use Swagger to call `GET /vector/search` with `q=PostgreSQL` and verify that
`Database Design` remains retrievable. Verify the notification with PostgreSQL:

```sql
SELECT feature_name, event_source, event_type, message, status, created_at
FROM notifications
ORDER BY notification_id DESC;
```

Expected values include `event_type = 'Knowledge Refresh'`,
`status = 'Unread'`, and the message `Knowledge Node regenerated successfully.`

## Expected error responses

- **503**: PostgreSQL is unavailable while the Event Monitor checks sources.
- **500**: Knowledge generation, embedding, vector sync, or notification
  creation failed. The response identifies the failing stage where available.

No scheduler, cron job, queue, or background worker runs this workflow. Only
`POST /automation/run` triggers it.
