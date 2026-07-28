import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const dist = resolve(root, "dist");
const templatePath = resolve(root, "worker", "template.js");
const dataPath = resolve(root, "data", "public_safe_data.json");
const hostingPath = resolve(root, ".openai", "hosting.json");
const token = "/*__ATLAS_DATA__*/null";

const [template, dataText] = await Promise.all([
  readFile(templatePath, "utf8"),
  readFile(dataPath, "utf8"),
]);
const parsed = JSON.parse(dataText);
if (parsed.release?.release_id !== "amp-evidence-atlas-v1.0-public-safe-beta") {
  throw new Error(`Unexpected release id: ${parsed.release?.release_id}`);
}
if (!template.includes(token)) throw new Error("Worker data injection token is missing.");
const worker = template.replace(token, dataText.trim());

await rm(dist, { recursive: true, force: true });
await mkdir(resolve(dist, "server"), { recursive: true });
await mkdir(resolve(dist, ".openai"), { recursive: true });
await writeFile(resolve(dist, "server", "index.js"), worker, "utf8");
await cp(hostingPath, resolve(dist, ".openai", "hosting.json"));
console.log(`Built ${dist} (${Buffer.byteLength(worker).toLocaleString()} worker bytes)`);
