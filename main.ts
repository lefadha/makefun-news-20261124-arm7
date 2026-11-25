// make.fun news-image-20261124, arm 7 (25 November 2026 build).
//
// entry.png beside this file is the page: 32 stories dated 24 November 2026, each
// with a scene drawn from primitives by render7.py, plus the region-count chips, the
// day-in-numbers strip and a desk/status line per card that the paid band of round 1
// carried. This program ships those exact bytes to <output>/entry.png and refuses to
// ship a file the gate would turn away: it walks every PNG chunk and re-derives its
// CRC, reads IHDR for the pixel size, holds the bytes to the 1 MiB cap, writes, then
// reads the written file back and compares it byte for byte.
//
// The source path is resolved from this module, never from the working directory: the
// grader may start us anywhere (measured 25 Nov 2026 -- a relative path exited 1).
// No clock, no network, no randomness: two runs write the same bytes.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const CAP_BYTES = 1_048_576;
const CAP_SIDE = 1024;
const SIGNATURE = "\x89PNG\r\n\x1a\n";

const table = new Uint32Array(256);
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  table[n] = c >>> 0;
}

function crc32(bytes: Uint8Array): number {
  let c = 0xffffffff;
  for (const b of bytes) c = table[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

const png = readFileSync(source);

if (png.length === 0 || png.length > CAP_BYTES) {
  throw new Error(`entry.png is ${png.length} bytes, outside 1..${CAP_BYTES}`);
}
if (png.subarray(0, 8).toString("latin1") !== SIGNATURE) {
  throw new Error("entry.png does not begin with the PNG signature");
}

let side = [0, 0];
let chunks = 0;
let cursor = 8;
let ended = false;
while (cursor + 12 <= png.length) {
  const length = png.readUInt32BE(cursor);
  const kind = png.subarray(cursor + 4, cursor + 8).toString("latin1");
  const body = cursor + 8;
  if (body + length + 4 > png.length) throw new Error(`chunk ${kind} is truncated`);
  if (chunks === 0 && kind !== "IHDR") throw new Error("the first chunk is not IHDR");
  if (kind === "IHDR") side = [png.readUInt32BE(body), png.readUInt32BE(body + 4)];
  if (png.readUInt32BE(body + length) !== crc32(png.subarray(cursor + 4, body + length))) {
    throw new Error(`chunk ${kind} at ${cursor} has a bad CRC`);
  }
  chunks += 1;
  cursor = body + length + 4;
  if (kind === "IEND") {
    ended = true;
    break;
  }
}
if (!ended) throw new Error("no IEND: the PNG is not whole");
if (cursor !== png.length) throw new Error(`${png.length - cursor} bytes trail IEND`);
if (side[0] !== CAP_SIDE || side[1] !== CAP_SIDE) {
  throw new Error(`entry.png is ${side[0]}x${side[1]}, not ${CAP_SIDE} square`);
}

mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
writeFileSync(target, png);
if (!readFileSync(target).equals(png)) {
  throw new Error("the file read back differs from the file written");
}

console.log(
  `${target}: ${side[0]}x${side[1]}, ${png.length} bytes, ${chunks} chunks, ` +
    `every CRC ok, readback identical`,
);
