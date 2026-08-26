"use strict";

const { app } = require("electron");
const http = require("node:http");
const { HardwareAgent } = require("./src/agent");

const HOST = "127.0.0.1";
const PORT = Number(process.env.HARDWARE_AGENT_PORT || 18765);
const TOKEN = process.env.HARDWARE_AGENT_TOKEN;

if (!TOKEN || TOKEN.length < 32) {
  throw new Error("HARDWARE_AGENT_TOKEN must be configured with at least 32 characters");
}

const agent = new HardwareAgent();

function authorized(request) {
  return request.headers.authorization === `Bearer ${TOKEN}`;
}

function send(response, status, body) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  });
  response.end(JSON.stringify(body));
}

function readJson(request) {
  return new Promise((resolve, reject) => {
    let data = "";
    request.setEncoding("utf8");
    request.on("data", (chunk) => {
      data += chunk;
      if (Buffer.byteLength(data, "utf8") > 1024 * 1024) {
        reject(new Error("request body too large"));
        request.destroy();
      }
    });
    request.on("end", () => {
      try {
        resolve(JSON.parse(data || "{}"));
      } catch {
        reject(new Error("invalid JSON"));
      }
    });
    request.on("error", reject);
  });
}

function createServer() {
  return http.createServer(async (request, response) => {
    if (!authorized(request)) return send(response, 401, { error: "unauthorized" });

    try {
      if (request.method === "GET" && request.url === "/health") {
        return send(response, 200, agent.health());
      }
      if (request.method !== "POST") return send(response, 405, { error: "method_not_allowed" });

      const payload = await readJson(request);
      if (request.url === "/v1/print") {
        const result = await agent.printReceipt(payload);
        return send(response, result.state === "completed" ? 200 : 503, result);
      }
      if (request.url === "/v1/cash-drawer/open") {
        const result = await agent.openCashDrawer(payload);
        return send(response, result.state === "completed" ? 200 : 503, result);
      }
      return send(response, 404, { error: "not_found" });
    } catch (error) {
      return send(response, 400, { error: error.message });
    }
  });
}

let server;
app.whenReady().then(() => {
  server = createServer();
  server.listen(PORT, HOST);
});

app.on("before-quit", () => {
  if (server) server.close();
});
