/**
 * Helpers for the wire-compat fixture produced by the Python service.
 * The fixture pins the on-disk format so JS and Python cannot drift
 * apart silently.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface FixtureMeta {
  numBits: number;
  numHashes: number;
  itemCount: number;
  generatedAtMillis: number;
  inserted: string[];
  absent: string[];
}

export function loadBloomFixture(): { blob: Uint8Array; meta: FixtureMeta } {
  const blob = new Uint8Array(
    readFileSync(resolve(__dirname, "bloom-snapshot.bin"))
  );
  const meta = JSON.parse(
    readFileSync(resolve(__dirname, "bloom-snapshot.json"), "utf8")
  ) as FixtureMeta;
  return { blob, meta };
}
