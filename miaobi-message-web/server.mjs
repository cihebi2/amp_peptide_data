import http from 'node:http';
import { createHash, randomUUID } from 'node:crypto';
import { createReadStream, existsSync, readdirSync, readFileSync, statSync, watch } from 'node:fs';
import { extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const __dirname = resolve(fileURLToPath(import.meta.url), '..');
const repoRoot = resolve(__dirname, '..');
const publicDir = join(__dirname, 'public');
const messageRoot = resolve(process.env.MIAOBI_MESSAGE_ROOT || join(repoRoot, '.miaobi-paper-review'));
const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 8765);

const socketsByWorkflow = new Map();
let lastEventSignature = new Map();

function sendJson(res, status, body) {
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
  });
  res.end(payload);
}

function sendText(res, status, body, contentType = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'content-type': contentType, 'cache-control': 'no-store' });
  res.end(body);
}

function readJson(path, fallback = null) {
  if (!existsSync(path)) return fallback;
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    return { _error: String(error), _path: path };
  }
}

function readJsonl(path) {
  if (!existsSync(path)) return [];
  const lines = readFileSync(path, 'utf8').split(/\r?\n/).filter(Boolean);
  const rows = [];
  for (let index = 0; index < lines.length; index += 1) {
    try {
      rows.push(JSON.parse(lines[index]));
    } catch (error) {
      rows.push({ record_type: 'parse_error', line: index + 1, error: String(error), raw: lines[index] });
    }
  }
  return rows;
}

function requireFs() {
  return globalThis.__batch4Fs ||= require('node:fs');
}

function artifactPathMaybeAbsolute(pathText) {
  if (!pathText) return '';
  return pathText.startsWith('/') ? pathText : join(repoRoot, pathText);
}

function loadReworkTickets(context) {
  const packetRoot = artifactPathMaybeAbsolute(context?.packet_root || '');
  if (!packetRoot) return [];
  const requests = readJsonl(join(packetRoot, 'rework', 'rework_requests.jsonl'));
  const responses = readJsonl(join(packetRoot, 'rework', 'rework_responses.jsonl'));
  const latestByTicket = new Map();
  for (const response of responses) {
    const ids = response.ticket_ids || (response.ticket_id ? [response.ticket_id] : []);
    for (const id of ids) latestByTicket.set(id, response);
  }
  return requests.map((ticket) => {
    const latest = latestByTicket.get(ticket.ticket_id);
    return {
      ...ticket,
      resolution_status: latest?.status || 'open',
      latest_response: latest || null,
    };
  });
}

function isOpenReworkTicket(ticket) {
  return !['resolved', 'closed'].includes(String(ticket?.resolution_status || 'open'));
}

function appendWorkflowRecord(id, filename, record) {
  const path = join(workflowBase(id), filename);
  const fs = requireFs();
  fs.mkdirSync(resolve(path, '..'), { recursive: true });
  fs.appendFileSync(path, `${JSON.stringify(record)}\n`, 'utf8');
}

function updateWorkflowContext(id, updater) {
  const path = join(workflowBase(id), 'workflow_context.json');
  const context = readJson(path, null);
  if (!context) return null;
  const next = updater(context) || context;
  next.updated_at = new Date().toISOString();
  const fs = requireFs();
  fs.writeFileSync(path, `${JSON.stringify(next, null, 2)}\n`, 'utf8');
  return next;
}

function readRequestBody(req) {
  return new Promise((resolveBody, reject) => {
    let data = '';
    req.on('data', chunk => {
      data += chunk;
      if (data.length > 1024 * 1024) {
        reject(new Error('request body too large'));
        req.destroy();
      }
    });
    req.on('end', () => {
      if (!data.trim()) resolveBody({});
      else {
        try { resolveBody(JSON.parse(data)); }
        catch (error) { reject(error); }
      }
    });
  });
}

function workflowBase(id) {
  return join(messageRoot, 'workflows', id);
}

function listWorkflowIds() {
  const dir = join(messageRoot, 'workflows');
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function loadWorkflow(id) {
  const base = workflowBase(id);
  const context = readJson(join(base, 'workflow_context.json'), null);
  if (!context) return null;
  const stateExecutions = readJsonl(join(base, 'state_executions.jsonl'));
  const chatMessages = readJsonl(join(base, 'chat_messages.jsonl'));
  const agentLogs = readJsonl(join(base, 'agent_logs.jsonl'));
  const artifacts = readJsonl(join(base, 'artifacts.jsonl'));
  const events = readJsonl(join(base, 'events.jsonl'));
  const reworkHistory = loadReworkTickets(context);
  const reworkTickets = reworkHistory.filter(isOpenReworkTicket);
  let updatedAt = context.updated_at || context.created_at || '';
  try {
    updatedAt = statSync(join(base, 'workflow_context.json')).mtime.toISOString();
  } catch {}
  return {
    id,
    workflowId: context.workflow_id,
    paperId: context.paper_id,
    title: context.metadata?.title || context.title || context.paper_id,
    context,
    stateExecutions,
    chatMessages,
    agentLogs,
    artifacts,
    events,
    reworkTickets,
    reworkHistory,
    updatedAt,
    counts: {
      states: stateExecutions.length,
      chat: chatMessages.length,
      logs: agentLogs.length,
      artifacts: artifacts.length,
      events: events.length,
      openRework: reworkTickets.length || (Array.isArray(context.open_rework_tickets) ? context.open_rework_tickets.length : 0),
      reworkHistory: reworkHistory.length,
    },
  };
}

function workflowSummary(wf) {
  const latestState = wf.stateExecutions.at(-1) || null;
  const latestEvent = wf.events.at(-1) || null;
  return {
    id: wf.id,
    workflowId: wf.workflowId,
    paperId: wf.paperId,
    title: wf.title,
    currentState: wf.context.current_state,
    queueStatus: wf.context.queue_status,
    gateSummary: wf.context.gate_summary,
    openReworkTickets: wf.context.open_rework_tickets || [],
    latestState,
    latestEvent,
    reworkTickets: wf.reworkTickets || [],
    reworkHistory: wf.reworkHistory || [],
    counts: wf.counts,
    updatedAt: wf.updatedAt,
  };
}

function sendFrame(socket, data) {
  const payload = Buffer.from(data);
  const len = payload.length;
  let header;
  if (len < 126) {
    header = Buffer.from([0x81, len]);
  } else if (len < 65536) {
    header = Buffer.alloc(4);
    header[0] = 0x81;
    header[1] = 126;
    header.writeUInt16BE(len, 2);
  } else {
    header = Buffer.alloc(10);
    header[0] = 0x81;
    header[1] = 127;
    header.writeBigUInt64BE(BigInt(len), 2);
  }
  socket.write(Buffer.concat([header, payload]));
}

function wsSend(socket, message) {
  sendFrame(socket, JSON.stringify(message));
}

function addSocket(workflowId, socket) {
  if (!socketsByWorkflow.has(workflowId)) socketsByWorkflow.set(workflowId, new Set());
  socketsByWorkflow.get(workflowId).add(socket);
  socket.on('close', () => socketsByWorkflow.get(workflowId)?.delete(socket));
  socket.on('error', () => socketsByWorkflow.get(workflowId)?.delete(socket));
}

function broadcast(workflowId, message) {
  for (const socket of socketsByWorkflow.get(workflowId) || []) {
    try { wsSend(socket, message); } catch { socketsByWorkflow.get(workflowId)?.delete(socket); }
  }
}

function eventSignature(wf) {
  return JSON.stringify({
    updatedAt: wf.updatedAt,
    counts: wf.counts,
    currentState: wf.context.current_state,
    gates: wf.context.gate_summary,
    queue: wf.context.queue_status,
  });
}

function pollAndBroadcast() {
  for (const id of listWorkflowIds()) {
    const wf = loadWorkflow(id);
    if (!wf) continue;
    const sig = eventSignature(wf);
    if (lastEventSignature.get(id) !== sig) {
      lastEventSignature.set(id, sig);
      broadcast(id, { type: 'workflow_snapshot', workflow: wf, summary: workflowSummary(wf), emittedAt: new Date().toISOString() });
    }
  }
}

function handleApi(req, res, pathname) {
  if (pathname === '/api/health') {
    sendJson(res, 200, { ok: true, messageRoot, repoRoot, now: new Date().toISOString() });
    return true;
  }
  if (pathname === '/api/workflows') {
    const workflows = listWorkflowIds().map((id) => loadWorkflow(id)).filter(Boolean).map(workflowSummary);
    sendJson(res, 200, { workflows, messageRoot });
    return true;
  }
  const actionMatch = pathname.match(/^\/api\/workflows\/([^/]+)\/actions$/);
  if (actionMatch) {
    if (req.method !== 'POST') {
      sendJson(res, 405, { error: 'method_not_allowed' });
      return true;
    }
    const id = decodeURIComponent(actionMatch[1]);
    readRequestBody(req).then((body) => {
      const wf = loadWorkflow(id);
      if (!wf) {
        sendJson(res, 404, { error: 'workflow_not_found', id });
        return;
      }
      const action = String(body.action || 'ack_rework');
      const state = String(body.state || wf.context.current_state || 'web_action');
      const message = String(body.message || (action === 'request_retry' ? `Web requested retry for ${state}` : `Web acknowledged rework/status for ${state}`));
      const createdAt = new Date().toISOString();
      appendWorkflowRecord(id, 'chat_messages.jsonl', {
        record_type: 'chat_message', workflow_id: wf.workflowId, paper_id: wf.paperId,
        state, role: 'reviewer', message, created_at: createdAt,
      });
      appendWorkflowRecord(id, 'events.jsonl', {
        record_type: 'workflow_event', workflow_id: wf.workflowId, paper_id: wf.paperId,
        state, event: action === 'request_retry' ? 'state_started' : 'state_completed',
        payload: { source: 'web_action', action, message }, created_at: createdAt,
      });
      updateWorkflowContext(id, (ctx) => {
        ctx.web_actions = [...(ctx.web_actions || []), { action, state, message, created_at: createdAt }].slice(-50);
        return ctx;
      });
      const next = loadWorkflow(id);
      if (next) broadcast(id, { type: 'workflow_snapshot', workflow: next, summary: workflowSummary(next), emittedAt: new Date().toISOString() });
      sendJson(res, 200, { ok: true, workflow: next });
    }).catch((error) => sendJson(res, 400, { error: 'bad_request', message: String(error.message || error) }));
    return true;
  }
  const match = pathname.match(/^\/api\/workflows\/([^/]+)$/);
  if (match) {
    const id = decodeURIComponent(match[1]);
    const wf = loadWorkflow(id);
    if (!wf) sendJson(res, 404, { error: 'workflow_not_found', id });
    else sendJson(res, 200, wf);
    return true;
  }
  return false;
}

function serveStatic(req, res, pathname) {
  const target = pathname === '/' ? join(publicDir, 'index.html') : join(publicDir, pathname);
  const resolved = resolve(target);
  if (!resolved.startsWith(publicDir) || !existsSync(resolved) || statSync(resolved).isDirectory()) {
    sendText(res, 404, 'Not found');
    return;
  }
  const contentType = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
  }[extname(resolved)] || 'application/octet-stream';
  res.writeHead(200, { 'content-type': contentType, 'cache-control': 'no-store' });
  createReadStream(resolved).pipe(res);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url || '/', `http://${req.headers.host || `${host}:${port}`}`);
  if (handleApi(req, res, url.pathname)) return;
  serveStatic(req, res, url.pathname);
});

server.on('upgrade', (req, socket) => {
  const url = new URL(req.url || '/', `http://${req.headers.host || `${host}:${port}`}`);
  const match = url.pathname.match(/^\/ws\/workflows\/([^/]+)$/);
  if (!match) {
    socket.destroy();
    return;
  }
  const key = req.headers['sec-websocket-key'];
  if (!key) {
    socket.destroy();
    return;
  }
  const accept = createHash('sha1').update(`${key}258EAFA5-E914-47DA-95CA-C5AB0DC85B11`).digest('base64');
  socket.write([
    'HTTP/1.1 101 Switching Protocols',
    'Upgrade: websocket',
    'Connection: Upgrade',
    `Sec-WebSocket-Accept: ${accept}`,
    '',
    '',
  ].join('\r\n'));
  const workflowId = decodeURIComponent(match[1]);
  addSocket(workflowId, socket);
  const wf = loadWorkflow(workflowId);
  wsSend(socket, { type: 'connected', connectionId: randomUUID(), workflowId, emittedAt: new Date().toISOString() });
  if (wf) wsSend(socket, { type: 'workflow_snapshot', workflow: wf, summary: workflowSummary(wf), emittedAt: new Date().toISOString() });
});

try {
  const workflowsDir = join(messageRoot, 'workflows');
  if (existsSync(workflowsDir)) watch(workflowsDir, { recursive: true }, () => setTimeout(pollAndBroadcast, 100));
} catch {
  // Recursive watch is not available on every filesystem; polling below is enough.
}
setInterval(pollAndBroadcast, 1500).unref();

server.listen(port, host, () => {
  console.log(`[miaobi-message-web] listening on http://${host}:${port}`);
  console.log(`[miaobi-message-web] messageRoot=${messageRoot}`);
});
