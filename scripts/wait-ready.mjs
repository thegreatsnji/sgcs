const url = "http://127.0.0.1:8000/ready/";
const maxAttempts = 40;
const delayMs = 3000;

async function sleep(ms) {
  await new Promise((r) => setTimeout(r, ms));
}

for (let i = 0; i < maxAttempts; i++) {
  try {
    const res = await fetch(url);
    if (res.ok) {
      console.log("Backend pronto:", url);
      process.exit(0);
    }
  } catch {
    /* retry */
  }
  await sleep(delayMs);
}

console.error("Timeout: backend não respondeu em /ready/");
process.exit(1);
