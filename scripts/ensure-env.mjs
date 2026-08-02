import { copyFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const env = join(root, ".env");
const example = join(root, ".env.example");

if (!existsSync(env) && existsSync(example)) {
  copyFileSync(example, env);
  console.log("Criado .env a partir de .env.example");
}
