#!/usr/bin/env node
// Copies generated PDFs from the build directory to a configurable output directory,
// renaming them from index.pdf to eclipse-threadx-<component>-<size>.pdf.
//
// Usage:
//   PDF_OUTPUT_DIR=/path/to/dir  node scripts/copy-pdfs.js
//   node scripts/copy-pdfs.js --output /path/to/dir

'use strict';

const fs   = require('fs');
const path = require('path');

// Resolve output directory from --output flag or PDF_OUTPUT_DIR env var.
const flagIndex = process.argv.indexOf('--output');
const outputDir = flagIndex !== -1 ? process.argv[flagIndex + 1] : process.env.PDF_OUTPUT_DIR;

if (!outputDir) {
  console.error('Error: no output directory specified.');
  console.error('  Set PDF_OUTPUT_DIR env var, or pass --output <dir>');
  process.exit(1);
}

const assemblerDir = path.resolve(__dirname, '..', 'build', 'assembler');

if (!fs.existsSync(assemblerDir)) {
  console.error(`Error: build directory not found: ${assemblerDir}`);
  console.error('Run the PDF build first: npm run build:pdf');
  process.exit(1);
}

const dest = path.resolve(outputDir);
fs.mkdirSync(dest, { recursive: true });

let copied = 0;

for (const size of fs.readdirSync(assemblerDir)) {
  const sizeDir = path.join(assemblerDir, size);
  if (!fs.statSync(sizeDir).isDirectory()) continue;

  for (const component of fs.readdirSync(sizeDir)) {
    const src = path.join(sizeDir, component, 'main', '_exports', 'index.pdf');
    if (!fs.existsSync(src)) continue;

    const destName = `eclipse-threadx-${component}-${size}.pdf`;
    fs.copyFileSync(src, path.join(dest, destName));
    console.log(`  ${destName}`);
    copied++;
  }
}

if (copied === 0) {
  console.warn('Warning: no PDFs found in the build directory.');
  process.exit(1);
}

console.log(`\n${copied} PDF(s) copied to: ${dest}`);
