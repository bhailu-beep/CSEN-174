// Runs before every test file: adds toBeInTheDocument() etc. and unmounts components after each test.
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());
