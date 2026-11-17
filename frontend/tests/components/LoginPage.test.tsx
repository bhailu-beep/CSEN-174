import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "@/app/login/page";

const push = vi.fn();
const login = vi.fn();

vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/components/AuthProvider", () => ({ useAuth: () => ({ login }) }));

beforeEach(() => {
  push.mockClear();
  login.mockReset();
});

function submit(username = "ada", password = "secret1") {
  render(<LoginPage />);
  fireEvent.change(screen.getByLabelText("Username"), { target: { value: username } });
  fireEvent.change(screen.getByLabelText("Password"), { target: { value: password } });
  fireEvent.click(screen.getByRole("button", { name: "Log In" }));
}

describe("LoginPage", () => {
  it("logs in and goes to the dashboard", async () => {
    login.mockResolvedValue(undefined);
    submit();
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
    expect(login).toHaveBeenCalledWith("ada", "secret1");
  });

  it("shows the backend's message for a wrong password and stays on the page", async () => {
    login.mockRejectedValue(new Error("Invalid username or password"));
    submit();
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid username or password");
    expect(push).not.toHaveBeenCalled();
  });

  it("disables the button while the request is in flight", async () => {
    let finish!: () => void;
    login.mockReturnValue(new Promise<void>((resolve) => { finish = resolve; }));
    submit();
    expect(screen.getByRole("button", { name: "Log In" })).toBeDisabled();
    finish();
    await waitFor(() => expect(push).toHaveBeenCalled());
  });

  it("has no demo account button", () => {
    render(<LoginPage />);
    expect(screen.queryByText(/demo/i)).not.toBeInTheDocument();
  });
});
