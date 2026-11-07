import {render, screen} from "@testing-library/react";

function TestComponent() {
    return <h1>Stillspace Test Environment</h1>;
}

test("renders a React component", () => {
    render(<TestComponent/>);

    expect(
        screen.getByRole("heading", {
            name: "Stillspace Test Environment",
        })
    ).toBeInTheDocument();
});