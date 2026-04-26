import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BoothFinder } from "./BoothFinder";


describe("BoothFinder", () => {
  it("renders GPS and manual search entry points", () => {
    render(<BoothFinder />);

    expect(
      screen.getByRole("heading", { name: /find your polling booth/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /use my current location/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/pincode or address/i)).toBeInTheDocument();
  });
});
