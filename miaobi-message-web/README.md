# Batch 4 Miaobi Message Web

This is a local, dependency-free port of the Miaobi message-transfer surface for Batch 4 paper review.

It mirrors the Miaobi workflow display contract described in `docs/MIAOBI_MESSAGE_TRANSFER_CONTRACT.md`:

- `workflow_context.json` as the workflow run/context snapshot.
- `state_executions.jsonl` as state execution replay.
- `chat_messages.jsonl` as the front-end conversation stream.
- `agent_logs.jsonl` as debug/tool/CLI logs.
- `artifacts.jsonl` as artifact path index.
- `events.jsonl` as websocket/replay events.

Run from the repository root:

```bash
PORT=8765 HOST=127.0.0.1 node miaobi-message-web/server.mjs
```

Open:

```text
http://127.0.0.1:8765/
```

Useful APIs:

```text
GET /api/health
GET /api/workflows
GET /api/workflows/<workflow-dir-name>
WS  /ws/workflows/<workflow-dir-name>
```

The web server reads `.miaobi-paper-review/workflows/` and does not modify paper evidence.

Rework actions:

```text
POST /api/workflows/<workflow-dir-name>/actions
Content-Type: application/json

{"action":"ack_rework","state":"adjudication","message":"reviewed in web panel"}
{"action":"request_retry","state":"analysis","message":"retry requested from web panel"}
```

The actions append `chat_messages.jsonl` and `events.jsonl`, update `workflow_context.web_actions`, and broadcast a new websocket snapshot. They do not automatically change scientific acceptance status.
