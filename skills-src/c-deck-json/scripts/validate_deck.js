#!/usr/bin/env node
/**
 * Validates an c-deck deck JSON file against the actual component
 * exports in src/SlideTemplates.jsx, so the allow-list never drifts from
 * the real renderer. Catches the failure mode where JsonSlideDeck silently
 * drops content because a `type` doesn't match any registered component.
 *
 * Usage: node validate_deck.js <path-to-deck.json>
 */
const fs = require('fs');
const path = require('path');

function findSlideTemplates(startDir) {
  let dir = startDir;
  for (let i = 0; i < 8; i++) {
    const candidate = path.join(dir, 'src', 'SlideTemplates.jsx');
    if (fs.existsSync(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

function loadAllowedTypes(slideTemplatesPath) {
  const src = fs.readFileSync(slideTemplatesPath, 'utf8');
  const names = new Set();
  const re = /export function (\w+)/g;
  let m;
  while ((m = re.exec(src))) names.add(m[1]);
  return names;
}

function collectTypes(node, pathStr, found, badContent) {
  if (Array.isArray(node)) {
    node.forEach((item, i) => collectTypes(item, `${pathStr}[${i}]`, found, badContent));
    return;
  }
  if (node && typeof node === 'object') {
    if (typeof node.type === 'string') {
      found.push({ type: node.type, path: pathStr });
    }
    if ('content' in node && node.content !== undefined && node.content !== null && !Array.isArray(node.content)) {
      badContent.push({ type: node.type, path: `${pathStr}.content`, value: node.content });
    }
    for (const key of Object.keys(node)) {
      if (key === 'type') continue;
      collectTypes(node[key], `${pathStr}.${key}`, found, badContent);
    }
  }
}

function main() {
  const file = process.argv[2];
  if (!file) {
    console.error('Usage: node validate_deck.js <path-to-deck.json>');
    process.exit(2);
  }

  const raw = fs.readFileSync(file, 'utf8');
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    console.error(`✗ Invalid JSON: ${e.message}`);
    process.exit(1);
  }

  if (!data || !Array.isArray(data.slides)) {
    console.error('✗ Deck is missing a top-level "slides" array.');
    process.exit(1);
  }

  const slideTemplatesPath = findSlideTemplates(path.dirname(path.resolve(file)))
    || findSlideTemplates(__dirname);
  if (!slideTemplatesPath) {
    console.error(
      '✗ Could not locate src/SlideTemplates.jsx by walking up from the deck file or this script. ' +
      'Run this from inside (or pass a deck path inside) the c-deck repo so the allow-list can be derived live.'
    );
    process.exit(2);
  }

  const allowed = loadAllowedTypes(slideTemplatesPath);
  const found = [];
  const badContent = [];
  collectTypes(data.slides, 'slides', found, badContent);

  const unknown = found.filter((f) => !allowed.has(f.type));
  const usedTypes = [...new Set(found.map((f) => f.type))].sort();

  console.log(`Slides: ${data.slides.length}`);
  console.log(`Distinct component types used: ${usedTypes.join(', ')}`);

  let failed = false;

  if (unknown.length > 0) {
    failed = true;
    console.error('\n✗ Unknown component type(s) — these will silently render nothing:');
    unknown.forEach((u) => console.error(`  - "${u.type}" at ${u.path}`));
    console.error(
      `\nAllowed types (from ${path.relative(process.cwd(), slideTemplatesPath)}):\n  ` +
      [...allowed].sort().join(', ')
    );
  }

  if (badContent.length > 0) {
    failed = true;
    console.error(
      '\n✗ Non-array "content" value(s) — JsonSlideDeck only renders content as children ' +
      'when it is a JSON array, so these will silently render NO body text/children at all ' +
      '(this includes the exact pattern shown in this repo\'s own README):'
    );
    badContent.forEach((b) => console.error(`  - ${b.path} on a "${b.type}" block, got: ${JSON.stringify(b.value)}`));
    console.error('\nFix: wrap each value in an array, e.g. "content": ["your text here"]');
  }

  if (failed) process.exit(1);

  console.log('\n✓ All component types are recognized and all "content" values are arrays.');
  process.exit(0);
}

main();
