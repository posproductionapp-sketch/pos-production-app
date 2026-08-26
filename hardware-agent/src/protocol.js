"use strict";

const MAX_RECEIPT_BYTES = 1024 * 1024;
const COMMAND_ID_PATTERN = /^[A-Za-z0-9._:-]{1,100}$/;

function assertCommandId(commandId) {
  if (typeof commandId !== "string" || !COMMAND_ID_PATTERN.test(commandId)) {
    throw new Error("invalid command_id");
  }
}

function assertReceipt(command) {
  assertCommandId(command.command_id);
  if (typeof command.store_id !== "string" || command.store_id.length < 1 || command.store_id.length > 36) {
    throw new Error("invalid store_id");
  }
  if (typeof command.receipt_id !== "string" || command.receipt_id.length < 1 || command.receipt_id.length > 100) {
    throw new Error("invalid receipt_id");
  }
  if (typeof command.content !== "string" || Buffer.byteLength(command.content, "utf8") > MAX_RECEIPT_BYTES) {
    throw new Error("invalid receipt content");
  }
}

function assertCashDrawer(command) {
  assertCommandId(command.command_id);
  if (typeof command.store_id !== "string" || command.store_id.length < 1 || command.store_id.length > 36) {
    throw new Error("invalid store_id");
  }
}

module.exports = { assertReceipt, assertCashDrawer, assertCommandId, MAX_RECEIPT_BYTES };
