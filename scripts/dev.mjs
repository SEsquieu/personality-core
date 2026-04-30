import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const host = process.env.PERSONALITY_CORE_HOST ?? "127.0.0.1";
const port = process.env.PERSONALITY_CORE_PORT ?? "8787";
const apiUrl = `http://${host}:${port}`;

let apiProcess;

async function main() {
  const apiReady = await isApiReady();
  if (!apiReady) {
    console.log(`[personality-core] API not detected at ${apiUrl}; starting it for the workbench.`);
    apiProcess = spawn(getPythonCommand(), ["-m", "personality_core.main", "serve", "--host", host, "--port", port], {
      cwd: process.cwd(),
      env: process.env,
      stdio: "inherit",
      shell: process.platform === "win32"
    });
    await waitForApi();
  } else {
    console.log(`[personality-core] API already running at ${apiUrl}.`);
  }

  const vite = spawn(process.execPath, ["node_modules/vite/bin/vite.js", "--host", "127.0.0.1"], {
    cwd: process.cwd(),
    env: process.env,
    stdio: "inherit",
    shell: false
  });

  vite.on("exit", (code, signal) => {
    if (apiProcess && !apiProcess.killed) apiProcess.kill();
    if (signal) process.kill(process.pid, signal);
    process.exit(code ?? 0);
  });
}

async function isApiReady() {
  try {
    const response = await fetch(`${apiUrl}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

async function waitForApi() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    if (await isApiReady()) return;
    await delay(500);
  }
  throw new Error(`Personality Core API did not become ready at ${apiUrl}.`);
}

function getPythonCommand() {
  return process.env.PERSONALITY_CORE_PYTHON ?? (process.platform === "win32" ? "python" : "python3");
}

process.on("SIGINT", () => {
  if (apiProcess && !apiProcess.killed) apiProcess.kill();
  process.exit(130);
});

main().catch((error) => {
  if (apiProcess && !apiProcess.killed) apiProcess.kill();
  console.error(`[personality-core] ${error.message}`);
  process.exit(1);
});
