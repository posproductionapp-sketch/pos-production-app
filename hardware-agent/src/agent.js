"use strict";

const { assertReceipt, assertCashDrawer } = require("./protocol");

class UnconfiguredPrinter {
  async print() {
    throw new Error("printer driver is not configured");
  }
}

class UnconfiguredCashDrawer {
  async open() {
    throw new Error("cash drawer driver is not configured");
  }
}

class HardwareAgent {
  constructor({ printer = new UnconfiguredPrinter(), cashDrawer = new UnconfiguredCashDrawer() } = {}) {
    this.printer = printer;
    this.cashDrawer = cashDrawer;
    this.completed = new Map();
  }

  async printReceipt(command) {
    assertReceipt(command);
    return this.#execute(command.command_id, () => this.printer.print(command));
  }

  async openCashDrawer(command) {
    assertCashDrawer(command);
    return this.#execute(command.command_id, () => this.cashDrawer.open(command));
  }

  health() {
    return {
      status: "ok",
      printer_configured: !(this.printer instanceof UnconfiguredPrinter),
      cash_drawer_configured: !(this.cashDrawer instanceof UnconfiguredCashDrawer),
    };
  }

  async #execute(commandId, operation) {
    const previous = this.completed.get(commandId);
    if (previous) return { ...previous, duplicate: true };

    try {
      await operation();
      const result = { command_id: commandId, state: "completed", duplicate: false };
      this.completed.set(commandId, result);
      return result;
    } catch (error) {
      const result = { command_id: commandId, state: "failed", duplicate: false, error: error.message };
      return result;
    }
  }
}

module.exports = { HardwareAgent, UnconfiguredPrinter, UnconfiguredCashDrawer };
