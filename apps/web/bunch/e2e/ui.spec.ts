import { test, expect } from "@playwright/test";

test.describe("UI and Theme", () => {
  test("should toggle between light and dark themes", async ({ page }) => {
    await page.goto("/");

    const initialTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains("dark")
        ? "dark"
        : "light";
    });

    await page.getByRole("button", { name: "Switch to dark mode" }).click();

    const newTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains("dark")
        ? "dark"
        : "light";
    });

    expect(newTheme).not.toBe(initialTheme);

    await page.getByRole("button", { name: "Switch to light mode" }).click();

    const finalTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains("dark")
        ? "dark"
        : "light";
    });

    expect(finalTheme).toBe(initialTheme);
  });
});
