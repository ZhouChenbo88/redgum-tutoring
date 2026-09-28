import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Scheduler, ValidationError } from './src/scheduler.js';

process.env.TZ ??= 'Australia/Brisbane';
const root = path.dirname(fileURLToPath(import.meta.url));
export function createServer(scheduler) {
  return http.createServer(async (request, response) => {
    const send = (status, value) => { response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }); response.end(JSON.stringify(value)); };
    try {
      const url = new URL(request.url, 'http://localhost');
      if (url.pathname.startsWith('/api/')) {
        if (['POST', 'PATCH', 'DELETE'].includes(request.method) && request.headers.origin) {
          let matches = false;
          try { matches = new URL(request.headers.origin).host === request.headers.host; } catch { /* Invalid origins are refused. */ }
          if (!matches) return send(403, { error: 'Write requests from a different origin are refused.' });
        }
        if (request.method === 'GET' && url.pathname === '/api/state') return send(200, scheduler.snapshot());
        if (request.method === 'GET' && url.pathname === '/api/schedule') return send(200, scheduler.view(Object.fromEntries(url.searchParams)));
        const match = /^\/api\/(students|tutors|windows|sessions)(?:\/([a-zA-Z0-9-]+))?$/.exec(url.pathname);
        if (!match) return send(404, { error: 'API route not found.' });
        const [, kind, id] = match;
        if (request.method === 'DELETE' && id) return send(200, scheduler.remove(kind, id));
        if (!((request.method === 'POST' && !id) || (request.method === 'PATCH' && id))) return send(405, { error: 'Method not supported.' });
        if (request.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') return send(415, { error: 'Use Content-Type application/json.' });
        let body = '';
        for await (const chunk of request) { body += chunk; if (Buffer.byteLength(body) > 65536) return send(413, { error: 'Request too large.' }); }
        let input;
        try { input = JSON.parse(body); } catch { return send(400, { error: 'Body must be valid JSON.' }); }
        if (!input || Array.isArray(input) || typeof input !== 'object') return send(400, { error: 'Body must be a JSON object.' });
        return send(request.method === 'POST' ? 201 : 200, request.method === 'POST' ? scheduler.create(kind, input) : scheduler.update(kind, id, input));
      }
      const files = { '/': ['index.html', 'text/html'], '/app.js': ['app.js', 'text/javascript'], '/style.css': ['style.css', 'text/css'] };
      if (request.method !== 'GET' || !files[url.pathname]) return send(404, { error: 'Page not found.' });
      const [filename, type] = files[url.pathname];
      response.writeHead(200, { 'Content-Type': `${type}; charset=utf-8`, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'" });
      response.end(fs.readFileSync(path.join(root, 'public', filename)));
    } catch (error) {
      if (!(error instanceof ValidationError)) console.error('Request failed:', error.message);
      send(error instanceof ValidationError ? 400 : 500, { error: error instanceof ValidationError ? error.message : 'Unable to save or load data. Check server logs and data-directory permissions.' });
    }
  });
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const scheduler = new Scheduler(path.resolve(process.env.DATA_FILE ?? path.join(root, 'data', 'schedule.json')));
  const host = process.env.HOST ?? '127.0.0.1';
  const port = Number(process.env.PORT ?? 3000);
  createServer(scheduler).listen(port, host, () => console.log(`Redgum desk: http://${host}:${port} (fictional local data; no authentication)`));
}
