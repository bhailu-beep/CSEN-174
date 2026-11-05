// Tests for saving code and progress in the browser (src/lib/storage/).
import { beforeEach, describe, expect, it } from "vitest";
import { findExercise } from "@/lib/exercises";
import { clearCode, loadCode, saveCode } from "@/lib/storage/codeStorage";
import { getSolved, getStatus, markSolved, resetProgress } from "@/lib/storage/progressStorage";

const sum = findExercise("sum-two-numbers")!;

beforeEach(() => localStorage.clear());

describe("codeStorage", () => {
  it("saves, loads, and clears code with the cpp-platform: prefix", () => {
    saveCode(sum.id, "int sum(int a, int b) { return a + b; }");
    expect(loadCode(sum.id)).toContain("return a + b");
    expect(localStorage.getItem("cpp-platform:code:sum")).not.toBeNull();
    clearCode(sum.id);
    expect(loadCode(sum.id)).toBeNull();
  });
});

describe("progressStorage", () => {
  it("starts as new", () => {
    expect(getStatus(sum)).toBe("new");
  });

  it("does not count unchanged starter code as started", () => {
    saveCode(sum.id, sum.starterCode);
    expect(getStatus(sum)).toBe("new");
  });

  it("marks edited code as started", () => {
    saveCode(sum.id, "int sum(int a, int b) { return 0; }");
    expect(getStatus(sum)).toBe("started");
  });

  it("marks solved once, without duplicates", () => {
    markSolved(sum.id);
    markSolved(sum.id);
    expect(getSolved()).toEqual(["sum"]);
    expect(getStatus(sum)).toBe("solved");
  });

  it("survives corrupted storage", () => {
    localStorage.setItem("cpp-platform:solved", "{not json");
    expect(getSolved()).toEqual([]);
  });

  it("resets solved marks and saved code", () => {
    markSolved(sum.id);
    saveCode(sum.id, "changed");
    resetProgress([sum]);
    expect(getSolved()).toEqual([]);
    expect(loadCode(sum.id)).toBeNull();
  });
});
