#!/usr/bin/env node
'use strict';

const fs = require('fs');
const crypto = require('crypto');
const https = require('https');

// --- Config ---
const SA_PATH = '/Users/jonathanbanner/.config/gcloud/agentcollect-seo.json';
const SITEMAP_PATH = '/Users/jonathanbanner/github/agentcollect/sitemap.xml';
const SCOPE = 'https://www.googleapis.com/auth/indexing';
const RATE_LIMIT_MS = 500; // 2 requests per second

// --- Helpers ---
function base64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function createJWT(sa) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'RS256', typ: 'JWT' };
  const payload = {
    iss: sa.client_email,
    scope: SCOPE,
    aud: sa.token_uri,
    iat: now,
    exp: now + 3600,
  };
  const segments = base64url(JSON.stringify(header)) + '.' + base64url(JSON.stringify(payload));
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(segments);
  const signature = sign.sign(sa.private_key);
  return segments + '.' + base64url(signature);
}

function httpsPost(url, body, headers) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname,
      path: u.pathname + u.search,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
    }, (res) => {
      let data = '';
      res.on('data', (c) => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

function extractUrls(xml) {
  const urls = [];
  const re = /<loc>(.*?)<\/loc>/g;
  let m;
  while ((m = re.exec(xml)) !== null) urls.push(m[1]);
  return urls;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// --- Main ---
async function main() {
  // 1. Load service account
  const sa = JSON.parse(fs.readFileSync(SA_PATH, 'utf8'));
  console.log(`Service account: ${sa.client_email}`);

  // 2. Create JWT and exchange for access token
  const jwt = createJWT(sa);
  console.log('Exchanging JWT for access token...');
  const tokenRes = await httpsPost(sa.token_uri, JSON.stringify({
    grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    assertion: jwt,
  }), { 'Content-Type': 'application/x-www-form-urlencoded' });

  // token_uri expects form-encoded, let's fix that
  const tokenRes2 = await new Promise((resolve, reject) => {
    const u = new URL(sa.token_uri);
    const formBody = `grant_type=${encodeURIComponent('urn:ietf:params:oauth:grant-type:jwt-bearer')}&assertion=${encodeURIComponent(jwt)}`;
    const req = https.request({
      hostname: u.hostname,
      path: u.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(formBody),
      },
    }, (res) => {
      let data = '';
      res.on('data', (c) => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.write(formBody);
    req.end();
  });

  if (tokenRes2.status !== 200) {
    console.error(`Token exchange failed (${tokenRes2.status}): ${tokenRes2.body}`);
    process.exit(1);
  }
  const { access_token } = JSON.parse(tokenRes2.body);
  console.log('Access token obtained.\n');

  // 3. Read sitemap and extract URLs
  const xml = fs.readFileSync(SITEMAP_PATH, 'utf8');
  const urls = extractUrls(xml);
  console.log(`Found ${urls.length} URLs in sitemap.xml\n`);

  // 4. Submit each URL
  let successes = 0;
  let failures = 0;
  const failedUrls = [];

  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    const body = JSON.stringify({ url, type: 'URL_UPDATED' });

    try {
      const res = await httpsPost(
        'https://indexing.googleapis.com/v3/urlNotifications:publish',
        body,
        { Authorization: `Bearer ${access_token}` }
      );
      const status = res.status;
      const short = url.replace('https://www.agentcollect.com', '');
      if (status === 200) {
        successes++;
        console.log(`[${i + 1}/${urls.length}] ${status} OK  ${short}`);
      } else {
        failures++;
        failedUrls.push({ url: short, status, detail: res.body.substring(0, 120) });
        console.log(`[${i + 1}/${urls.length}] ${status} FAIL ${short}`);
      }
    } catch (err) {
      failures++;
      failedUrls.push({ url, status: 'ERR', detail: err.message });
      console.log(`[${i + 1}/${urls.length}] ERR  ${url} — ${err.message}`);
    }

    // Rate limit: 500ms between requests = 2/sec
    if (i < urls.length - 1) await sleep(RATE_LIMIT_MS);
  }

  // 5. Summary
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total URLs:  ${urls.length}`);
  console.log(`Successes:   ${successes}`);
  console.log(`Failures:    ${failures}`);
  if (failedUrls.length > 0) {
    console.log('\nFailed URLs:');
    failedUrls.forEach(f => console.log(`  ${f.status} ${f.url} — ${f.detail}`));
  }
  console.log('='.repeat(60));
}

main().catch(err => { console.error('Fatal:', err); process.exit(1); });
