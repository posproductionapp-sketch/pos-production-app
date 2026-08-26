"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { HardwareAgent } = require("../src/agent");

test("hardware commands are idempotent by command id", async () => {
  let printCount = 0;
  const agent = new HardwareAgent({
    printer: { print: async () => { printCount += 1; } },
    cashDrawer: { open: async () => {} },
  });

  const command = {
    command_id: "print-1",
    store_id: "store",
    receipt_id: "receipt-1",
    content: "receipt",
  };

  assert.deepEqual(await agent.printReceipt(command), {
    command_id: "print-1",
    state: "completed",
    duplicate: false,
  });
  assert.deepEqual(await agent.printReceipt(command), {
    command_id: "print-1",
    state: "completed",
    duplicate: true,
  });
  assert.equal(printCount, 1);
});

test("unconfigured hardware fails closed", async () => {
  const agent = new HardwareAgent();
  const result = await agent.openCashDrawer({ command_id: "drawer-1", store_id: "store" });
  assert.equal(result.state, "failed");
  assert.match(result.error, /not configured/);
});

test("receipt payload validation rejects oversized content", async () => {
  const agent = new HardwareAgent({ printer: { print: async () => {} } });
  const result = await agent.printReceipt({
    command_id: "print-2",
    store_id: "store",
    receipt_id: "receipt-2",
    content: "x".repeat(1024 * 1024 + 1),
  }).catch((error) => error);
  assert.equal(result.message, "invalid receipt content");
});
