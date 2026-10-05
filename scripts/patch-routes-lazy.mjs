import fs from "fs";
import path from "path";

const indexPath = path.join(process.cwd(), "frontend/src/routes/index.tsx");
const lazyPath = path.join(process.cwd(), "frontend/src/routes/pages.lazy.ts");
let text = fs.readFileSync(indexPath, "utf8");

const lazyText = fs.readFileSync(lazyPath, "utf8");
const exportNames = [...lazyText.matchAll(/^export const (\w+) =/gm)].map((m) => m[1]);
if (exportNames.length === 0) {
  console.error("No lazy exports found");
  process.exit(1);
}

const start = text.indexOf("import { PatientClinicalPage");
const end = text.indexOf('import { ProtectedRoute');
if (start === -1 || end === -1) {
  console.error("Could not find import block to replace");
  process.exit(1);
}

const lazyImport =
  `import {\n  ${exportNames.join(",\n  ")},\n} from "@/routes/pages.lazy";\n\n`;

text = text.slice(0, start) + lazyImport + text.slice(end);

for (const name of exportNames) {
  const re = new RegExp(`<${name}(\\s|/|>)`, "g");
  text = text.replace(re, `<${name}$1`);
}

fs.writeFileSync(indexPath, text);
console.log(`Patched index.tsx with ${exportNames.length} lazy imports`);
