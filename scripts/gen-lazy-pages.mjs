import fs from "fs";
import path from "path";

const indexPath = path.join(process.cwd(), "frontend/src/routes/index.tsx");
const text = fs.readFileSync(indexPath, "utf8");
const lines = [
  'import { lazy, type ComponentType } from "react";',
  "",
  "function lazyNamed<M extends Record<string, ComponentType<unknown>>>(",
  "  loader: () => Promise<M>,",
  "  name: keyof M & string,",
  ") {",
  "  return lazy(() => loader().then((m) => ({ default: m[name] as ComponentType<unknown> })));",
  "}",
  "",
];

const seen = new Set();

function addExport(binding, exportName, pathStr) {
  if (!binding || !exportName || seen.has(binding)) return;
  if (pathStr.includes("/layouts/")) return;
  seen.add(binding);
  lines.push(
    `export const ${binding} = lazyNamed(() => import("${pathStr}"), "${exportName}");`,
  );
}

const blockRe = /import\s+\{([^}]+)\}\s+from\s+["'](@\/[^"']+)["'];?/g;
let block;
while ((block = blockRe.exec(text)) !== null) {
  const spec = block[1];
  const pathStr = block[2];
  if (pathStr.includes("/routes/")) continue;
  for (const part of spec.split(",")) {
    const trimmed = part.trim();
    const asMatch = trimmed.match(/^(\w+)\s+as\s+(\w+)$/);
    if (asMatch) {
      addExport(asMatch[2], asMatch[1], pathStr);
    } else {
      const name = trimmed.match(/^(\w+)/)?.[1];
      if (name) addExport(name, name, pathStr);
    }
  }
}

const outPath = path.join(process.cwd(), "frontend/src/routes/pages.lazy.ts");
fs.writeFileSync(outPath, `${lines.join("\n")}\n`);
console.log(`Wrote ${seen.size} lazy exports to ${outPath}`);
