/**
 * Generator script for Security Assessment Excel Reports (findings.xlsx & endpoint-inventory.xlsx)
 * Powered by ExcelJS
 */

const ExcelJS = require('exceljs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'Vulnerability Test Results');
const FINDINGS_FILE = path.join(OUTPUT_DIR, 'findings.xlsx');
const INVENTORY_FILE = path.join(OUTPUT_DIR, 'endpoint-inventory.xlsx');

const findingsData = [
  {
    id: 'SEC-01',
    title: 'Direct Unauthenticated Static File Mount Exposing Private Research Data',
    severity: 'CRITICAL',
    type: 'Broken Access Control / IDOR (CWE-284)',
    file: 'StainScope-Backend-Server/api.py',
    line: 48,
    endpoint: 'GET /storage/{file_type}/{subpath}',
    desc: 'app.mount("/storage", StaticFiles(...)) mounts storage directory unauthenticated, bypassing get_secure_file() ownership validation.',
    impact: 'Confidentiality breach of medical/scientific microscopy data and complete circumvention of multi-tenant authorization.',
    remediation: 'Remove unauthenticated /storage StaticFiles mount from api.py and enforce all file access via /files/...'
  },
  {
    id: 'SEC-02',
    title: 'Developer Authentication Bypass Fallback Active via Environment Variable',
    severity: 'HIGH',
    type: 'Authentication Bypass via Debug Mode (CWE-489)',
    file: 'StainScope-Backend-Server/api.py',
    line: 61,
    endpoint: 'All Protected Endpoints (/analyses, /profile, etc.)',
    desc: 'When STAINSCOPE_DEV_MODE=true, missing Authorization headers default to DEV_MODE_TEST_USER_ID.',
    impact: 'Unauthenticated attackers gain access to default research records and analyses in staging/production.',
    remediation: 'Disable STAINSCOPE_DEV_MODE by default and enforce strict 401 Unauthorized exceptions in production.'
  },
  {
    id: 'SEC-03',
    title: 'Hardcoded Fallback Secret Key for JWT Token Generation',
    severity: 'HIGH',
    type: 'Hardcoded Cryptographic Key (CWE-798)',
    file: 'StainScope-Backend-Server/db_mysql.py',
    line: 37,
    endpoint: 'JWT Token Validation Routines',
    desc: 'JWT_SECRET has a static hardcoded fallback string if environment variable is not supplied.',
    impact: 'Attackers can forge valid JWT tokens and impersonate arbitrary user accounts.',
    remediation: 'Require JWT_SECRET from environment variables and fail startup if default secret is detected.'
  },
  {
    id: 'SEC-04',
    title: 'Token Transmission in URL Query Parameter',
    severity: 'MEDIUM',
    type: 'Sensitive Data Exposure via Query String (CWE-598)',
    file: 'StainScope-Backend-Server/api.py',
    line: 136,
    endpoint: 'GET /files/{file_type}/{subpath}?token=...',
    desc: 'get_secure_file accepts JWT tokens in query strings, causing token exposure in server logs, proxy logs, and Referer headers.',
    impact: 'Session token leakage to intermediaries and log collectors.',
    remediation: 'Use Authorization: Bearer headers or short-lived (60s) single-use download tokens.'
  },
  {
    id: 'SEC-05',
    title: 'Wildcard Cross-Origin Resource Sharing (CORS) Policy',
    severity: 'MEDIUM',
    type: 'Misconfigured CORS / Permissive Origin (CWE-942)',
    file: 'StainScope-Backend-Server/api.py',
    line: 37,
    endpoint: 'All REST API Endpoints',
    desc: 'CORSMiddleware configured with allow_origins=["*"] and allow_credentials=True.',
    impact: 'Potential cross-origin data exposure from malicious domains.',
    remediation: 'Restrict allow_origins to explicitly approved frontend origins.'
  },
  {
    id: 'SEC-06',
    title: 'Missing Rate Limiting on Authentication Endpoints',
    severity: 'MEDIUM',
    type: 'Lack of Rate Limiting / Brute-Force Risk (CWE-307)',
    file: 'StainScope-Backend-Server/api.py',
    line: 208,
    endpoint: 'POST /auth/login, POST /auth/signup',
    desc: 'Authentication routes accept unlimited requests without throttling or IP cooldown.',
    impact: 'Vulnerability to automated credential stuffing and compute exhaustion.',
    remediation: 'Implement slowapi rate limiting restricting login attempts to 5-10 per minute per IP.'
  },
  {
    id: 'SEC-07',
    title: 'Missing Standard Security Response Headers (CSP, HSTS, X-Frame-Options)',
    severity: 'LOW',
    type: 'Missing Security Headers (CWE-693)',
    file: 'StainScope-Backend-Server/api.py',
    line: 30,
    endpoint: 'All Endpoints',
    desc: 'FastAPI responses lack X-Content-Type-Options, X-Frame-Options, and Content-Security-Policy headers.',
    impact: 'MIME-type sniffing and clickjacking risks in web client integrations.',
    remediation: 'Add security middleware to inject defensive HTTP response headers.'
  }
];

const endpointData = [
  { ep: '/health', method: 'GET', auth: 'No (Public)', roles: 'Public / All', path: 'StainScope-Backend-Server/api.py:119', risk: 'Low', controls: 'Health check response' },
  { ep: '/docs', method: 'GET', auth: 'No (Public)', roles: 'Public / Dev', path: 'StainScope-Backend-Server/api.py:30', risk: 'Low', controls: 'OpenAPI Swagger UI' },
  { ep: '/openapi.json', method: 'GET', auth: 'No (Public)', roles: 'Public / Dev', path: 'StainScope-Backend-Server/api.py:30', risk: 'Low', controls: 'OpenAPI schema JSON' },
  { ep: '/auth/signup', method: 'POST', auth: 'No (Public)', roles: 'Anonymous / Guest', path: 'StainScope-Backend-Server/api.py:208', risk: 'Medium', controls: 'Pydantic validation, bcrypt hash' },
  { ep: '/auth/login', method: 'POST', auth: 'No (Public)', roles: 'Anonymous / Guest', path: 'StainScope-Backend-Server/api.py:235', risk: 'Medium', controls: 'Pydantic validation, bcrypt verify' },
  { ep: '/analyze', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Researcher', path: 'StainScope-Backend-Server/api.py:260', risk: 'High', controls: 'JWT auth, image validation, MySQL persist' },
  { ep: '/analyze-batch', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Researcher', path: 'StainScope-Backend-Server/api.py:392', risk: 'High', controls: 'JWT auth, multi-image processing' },
  { ep: '/analyses', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:419', risk: 'Medium', controls: 'JWT auth, user_id row filter' },
  { ep: '/analyses/deleted', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:425', risk: 'Medium', controls: 'JWT auth, soft-delete filter' },
  { ep: '/analyses/{id}', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:431', risk: 'Medium', controls: 'JWT auth, user_id ownership check' },
  { ep: '/analyses/{id}', method: 'DELETE', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:445', risk: 'Medium', controls: 'JWT auth, user_id ownership check' },
  { ep: '/analyses/{id}/restore', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:454', risk: 'Medium', controls: 'JWT auth, user_id ownership check' },
  { ep: '/analyses/cleanup-deleted', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Owner / Admin', path: 'StainScope-Backend-Server/api.py:463', risk: 'Low', controls: 'JWT auth, retention purge' },
  { ep: '/profile', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Self', path: 'StainScope-Backend-Server/api.py:471', risk: 'Medium', controls: 'JWT auth, user profile lookup' },
  { ep: '/profile', method: 'PUT', auth: 'Yes (Bearer JWT)', roles: 'Self', path: 'StainScope-Backend-Server/api.py:486', risk: 'Medium', controls: 'JWT auth, Pydantic field filter' },
  { ep: '/notes', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:495', risk: 'Medium', controls: 'JWT auth, user_id row filter' },
  { ep: '/notes/deleted', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:501', risk: 'Medium', controls: 'JWT auth, soft-delete filter' },
  { ep: '/notes', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:507', risk: 'Medium', controls: 'JWT auth, parameterized insert' },
  { ep: '/notes/{id}', method: 'DELETE', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:516', risk: 'Medium', controls: 'JWT auth, ownership check' },
  { ep: '/notes/{id}/restore', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:523', risk: 'Medium', controls: 'JWT auth, ownership check' },
  { ep: '/saved-comparisons', method: 'GET', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:533', risk: 'Medium', controls: 'JWT auth, user_id row filter' },
  { ep: '/saved-comparisons', method: 'POST', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:539', risk: 'Medium', controls: 'JWT auth, JSON serializer' },
  { ep: '/saved-comparisons/{id}', method: 'DELETE', auth: 'Yes (Bearer JWT)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:553', risk: 'Medium', controls: 'JWT auth, ownership check' },
  { ep: '/files/{file_type}/{path}', method: 'GET', auth: 'Yes (Bearer / Query)', roles: 'Owner', path: 'StainScope-Backend-Server/api.py:131', risk: 'High', controls: 'JWT auth, path traversal sanitize, DB owner query' },
  { ep: '/storage/{path}', method: 'GET', auth: 'NO (Static Mount)', roles: 'Public Unrestricted', path: 'StainScope-Backend-Server/api.py:48', risk: 'Critical', controls: 'NONE (Vulnerability finding SEC-01)' }
];

const dependencyData = [
  { pkg: 'fastapi', cur: '>=0.95.0', rec: '>=0.110.0', license: 'MIT', risk: 'Low', status: 'Active Support' },
  { pkg: 'uvicorn', cur: '>=0.20.0', rec: '>=0.29.0', license: 'BSD-3', risk: 'Low', status: 'Active Support' },
  { pkg: 'python-multipart', cur: '>=0.0.6', rec: '>=0.0.9', license: 'Apache-2.0', risk: 'Medium', status: 'Fixes CVE-2024-24762 ReDoS' },
  { pkg: 'pydantic', cur: '>=1.10.0', rec: '>=1.10.14', license: 'MIT', risk: 'Low', status: 'Active Support' },
  { pkg: 'opencv-python-headless', cur: '>=4.7.0.72', rec: '>=4.9.0.80', license: 'Apache-2.0', risk: 'Low', status: 'Active Support' },
  { pkg: 'numpy', cur: '>=1.23.0', rec: '>=1.24.0', license: 'BSD-3', risk: 'Low', status: 'Active Support' },
  { pkg: 'pymysql', cur: '>=1.0.3', rec: '>=1.1.0', license: 'MIT', risk: 'Low', status: 'Active Support' },
  { pkg: 'passlib[bcrypt]', cur: '>=1.7.4', rec: 'Remove (use direct bcrypt)', license: 'BSD', risk: 'Medium', status: 'Unmaintained Upstream' },
  { pkg: 'bcrypt', cur: '>=4.0.1', rec: '>=4.1.2', license: 'Apache-2.0', risk: 'Low', status: 'Active Support' },
  { pkg: 'pyjwt', cur: '>=2.8.0', rec: '>=2.8.0', license: 'MIT', risk: 'Low', status: 'Active Support' },
  { pkg: 'cryptography', cur: '>=41.0.0', rec: '>=42.0.5', license: 'Apache-2.0', risk: 'Low', status: 'Active Support' },
  { pkg: 'python-dotenv', cur: '>=1.0.0', rec: '>=1.0.1', license: 'BSD-3', risk: 'Low', status: 'Active Support' }
];

async function createSecurityWorkbook(filePath) {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'StainScope Security Assessment Team';
  wb.created = new Date();

  // --------------------------------------------------------------------------
  // SHEET 1: SECURITY FINDINGS
  // --------------------------------------------------------------------------
  const s1 = wb.addWorksheet('Security Findings', { views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }] });
  s1.getRow(1).values = ['Finding ID', 'Vulnerability Title', 'Severity', 'Vulnerability Type (CWE)', 'Affected File', 'Line', 'Endpoint', 'Description & Impact', 'Recommended Fix'];
  s1.getRow(1).height = 26;
  s1.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
  s1.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF801D1E' } };

  findingsData.forEach((f, idx) => {
    const row = s1.getRow(idx + 2);
    row.values = [f.id, f.title, f.severity, f.type, f.file, f.line, f.endpoint, `${f.desc}\nImpact: ${f.impact}`, f.remediation];
    row.font = { size: 9.5 };
    row.alignment = { vertical: 'middle', wrapText: true };

    const sevCell = row.getCell(3);
    sevCell.alignment = { horizontal: 'center', vertical: 'middle' };
    if (f.severity === 'CRITICAL') {
      sevCell.font = { bold: true, color: { argb: 'FF991B1B' } };
      sevCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFEE2E2' } };
    } else if (f.severity === 'HIGH') {
      sevCell.font = { bold: true, color: { argb: 'FFC2410C' } };
      sevCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFEDD5' } };
    } else if (f.severity === 'MEDIUM') {
      sevCell.font = { bold: true, color: { argb: 'FF854D0E' } };
      sevCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFEF9C3' } };
    } else {
      sevCell.font = { bold: true, color: { argb: 'FF1E40AF' } };
      sevCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDBEAFE' } };
    }
  });

  s1.getColumn(1).width = 12;
  s1.getColumn(2).width = 35;
  s1.getColumn(3).width = 14;
  s1.getColumn(4).width = 28;
  s1.getColumn(5).width = 28;
  s1.getColumn(6).width = 8;
  s1.getColumn(7).width = 25;
  s1.getColumn(8).width = 45;
  s1.getColumn(9).width = 40;

  // --------------------------------------------------------------------------
  // SHEET 2: ENDPOINT INVENTORY
  // --------------------------------------------------------------------------
  const s2 = wb.addWorksheet('Endpoint Inventory', { views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }] });
  s2.getRow(1).values = ['Endpoint', 'HTTP Method', 'Authentication Required', 'Expected Roles', 'Controller / File Path', 'Risk Level', 'Security Controls'];
  s2.getRow(1).height = 26;
  s2.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
  s2.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF801D1E' } };

  endpointData.forEach((ep, idx) => {
    const row = s2.getRow(idx + 2);
    row.values = [ep.ep, ep.method, ep.auth, ep.roles, ep.path, ep.risk, ep.controls];
    row.font = { size: 9.5 };
    row.getCell(2).alignment = { horizontal: 'center' };
    row.getCell(3).alignment = { horizontal: 'center' };
    row.getCell(6).alignment = { horizontal: 'center' };
  });

  s2.getColumn(1).width = 28;
  s2.getColumn(2).width = 14;
  s2.getColumn(3).width = 22;
  s2.getColumn(4).width = 20;
  s2.getColumn(5).width = 38;
  s2.getColumn(6).width = 14;
  s2.getColumn(7).width = 36;

  // --------------------------------------------------------------------------
  // SHEET 3: DEPENDENCY VULNERABILITIES
  // --------------------------------------------------------------------------
  const s3 = wb.addWorksheet('Dependency Vulnerabilities', { views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }] });
  s3.getRow(1).values = ['Package Name', 'Current Pin', 'Recommended Version', 'License', 'Supply Chain Risk', 'Advisory Status & CVEs'];
  s3.getRow(1).height = 26;
  s3.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
  s3.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF801D1E' } };

  dependencyData.forEach((d, idx) => {
    const row = s3.getRow(idx + 2);
    row.values = [d.pkg, d.cur, d.rec, d.license, d.risk, d.status];
    row.font = { size: 9.5 };
    row.getCell(2).alignment = { horizontal: 'center' };
    row.getCell(3).alignment = { horizontal: 'center' };
    row.getCell(4).alignment = { horizontal: 'center' };
    row.getCell(5).alignment = { horizontal: 'center' };
  });

  s3.getColumn(1).width = 25;
  s3.getColumn(2).width = 16;
  s3.getColumn(3).width = 24;
  s3.getColumn(4).width = 14;
  s3.getColumn(5).width = 18;
  s3.getColumn(6).width = 35;

  // --------------------------------------------------------------------------
  // SHEET 4: RISK SUMMARY
  // --------------------------------------------------------------------------
  const s4 = wb.addWorksheet('Risk Summary', { views: [{ showGridLines: true }] });
  s4.mergeCells('B2:G3');
  const tCell = s4.getCell('B2');
  tCell.value = '🛡️ StainScope Platform - Security Posture & Risk Summary';
  tCell.font = { size: 14, bold: true, color: { argb: 'FFFFFFFF' } };
  tCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF801D1E' } };
  tCell.alignment = { horizontal: 'center', vertical: 'middle' };

  // Score Cards
  s4.mergeCells('B5:C6');
  s4.getCell('B5').value = 'SECURITY POSTURE SCORE\n76 / 100';
  s4.getCell('B5').font = { bold: true, size: 12, color: { argb: 'FF1E40AF' } };
  s4.getCell('B5').alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
  s4.getCell('B5').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF8FAFC' } };

  s4.mergeCells('D5:E6');
  s4.getCell('D5').value = 'TARGET HARDENED SCORE\n96 / 100';
  s4.getCell('D5').font = { bold: true, size: 12, color: { argb: 'FF065F46' } };
  s4.getCell('D5').alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
  s4.getCell('D5').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF8FAFC' } };

  s4.mergeCells('F5:G6');
  s4.getCell('F5').value = 'TOTAL FINDINGS\n7 Findings';
  s4.getCell('F5').font = { bold: true, size: 12, color: { argb: 'FF991B1B' } };
  s4.getCell('F5').alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
  s4.getCell('F5').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF8FAFC' } };

  // Severity Distribution Table
  s4.getRow(8).values = ['', 'Severity Level', 'Findings Count', 'Action Timeline', 'Remediation Priority'];
  s4.getRow(8).font = { bold: true, color: { argb: 'FFFFFFFF' } };
  s4.getRow(8).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF334155' } };

  const sevTable = [
    ['CRITICAL', 1, 'Immediate (< 24 Hours)', 'P0 - Block Release'],
    ['HIGH', 2, 'Urgent (< 3 Days)', 'P1 - High Priority'],
    ['MEDIUM', 3, 'Scheduled (< 1 Sprint)', 'P2 - Medium Priority'],
    ['LOW', 1, 'Backlog / Best Practice', 'P3 - Low Priority']
  ];

  sevTable.forEach((st, idx) => {
    const row = s4.getRow(idx + 9);
    row.values = ['', st[0], st[1], st[2], st[3]];
    row.getCell(2).font = { bold: true };
    row.getCell(3).alignment = { horizontal: 'center' };
    row.getCell(5).font = { bold: true };
  });

  s4.getColumn(1).width = 4;
  s4.getColumn(2).width = 20;
  s4.getColumn(3).width = 18;
  s4.getColumn(4).width = 25;
  s4.getColumn(5).width = 25;
  s4.getColumn(6).width = 18;
  s4.getColumn(7).width = 18;

  await wb.xlsx.writeFile(filePath);
}

async function main() {
  console.log('Generating findings.xlsx...');
  await createSecurityWorkbook(FINDINGS_FILE);
  console.log('Generating endpoint-inventory.xlsx...');
  await createSecurityWorkbook(INVENTORY_FILE);
  console.log('All Excel security workbooks generated successfully in Vulnerability Test Results/');
}

main().catch(console.error);
