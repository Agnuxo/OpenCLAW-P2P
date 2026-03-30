const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.P2PCLAW_API_BASE || 'https://api-production-ff1b.up.railway.app';
const PAPER_PATH = path.join(__dirname, '../papers/P2PCLAW_Silicon_Lab_2026.md');

async function main() {
  const content = fs.readFileSync(PAPER_PATH, 'utf8');
  const payload = {
    title: 'OpenCLAW-P2P / P2PCLAW: Scientific Reproducible Evaluation (2026)',
    author: 'Codex-Research-Agent',
    agentId: 'Codex-Research-Agent',
    content,
    investigation: 'P2PCLAW-Silicon-Lab-2026'
  };

  console.log('Publishing paper...');
  console.log(`Endpoint: ${BASE_URL}/publish-paper`);
  console.log(`Chars: ${content.length}`);
  console.log(`Words: ${content.split(/\s+/).length}`);

  const response = await fetch(`${BASE_URL}/publish-paper`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const text = await response.text();
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    parsed = { raw: text };
  }

  console.log(`HTTP ${response.status}`);
  console.log(JSON.stringify(parsed, null, 2));

  if (!response.ok) process.exit(1);
}

main().catch((err) => {
  console.error('Publication failed:', err);
  process.exit(1);
});
