// Tests for the prototype login in src/lib/auth.ts.
import { beforeEach, describe, expect, it } from "vitest";
import { currentUser, DEMO_PASSWORD, DEMO_USERNAME, login, logout, signup } from "@/lib/auth";

beforeEach(() => localStorage.clear());

describe("prototype login (username + password, no email)", () => {
  it("logs in with the demo account", () => {
    expect(login(DEMO_USERNAME, DEMO_PASSWORD)).toBe(true);
    expect(currentUser()).toBe("student");
  });

  it("signs up, logs out, and logs back in", () => {
    expect(signup("bemmy_h", "secret1")).toBeNull();
    expect(currentUser()).toBe("bemmy_h");
    logout();
    expect(currentUser()).toBeNull();
    expect(login("BEMMY_H", "secret1")).toBe(true);
  });

  it("rejects a wrong password", () => {
    signup("lori", "secret1");
    logout();
    expect(login("lori", "wrong12")).toBe(false);
  });

  it("validates username, password, and duplicates", () => {
    expect(signup("ab", "secret1")).toMatch(/Username/);
    expect(signup("has space", "secret1")).toMatch(/Username/);
    expect(signup("zack", "123")).toMatch(/Password/);
    signup("zack", "secret1");
    expect(signup("ZACK", "secret1")).toMatch(/taken/);
    expect(signup("student", "secret1")).toMatch(/taken/);
  });
});
