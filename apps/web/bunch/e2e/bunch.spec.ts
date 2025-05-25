import { expect, test } from "@playwright/test";

test.describe("Bunch Management", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  // test("create a new bunch and verify no channels exist", async ({ page }) => {
  //   await page.locator(".w-12 > .inline-flex").first().click();

  //   await page.getByRole("textbox", { name: "Name" }).click();
  //   await page.getByRole("textbox", { name: "Name" }).fill("Test Bunch");
  //   await page.getByRole("textbox", { name: "Description" }).click();
  //   await page
  //     .getByRole("textbox", { name: "Description" })
  //     .fill("A test bunch for e2e testing");
  //   await page.getByRole("button", { name: "Create Bunch" }).click();

  //   await page.getByRole("link", { name: "Te" }).click();

  //   await expect(
  //     page.getByRole("heading", { name: "Test Bunch" })
  //   ).toBeVisible();

  //   await expect(page.getByText("No text channels yet")).toBeVisible();
  //   await expect(
  //     page.getByRole("button", { name: "Create a channel" })
  //   ).toBeVisible();
  // });

  test("should show bunch creation dialog when clicking create bunch button", async ({
    page,
  }) => {
    await page
      .getByRole("button", { name: /Create Bunch/i })
      .first()
      .click();

    const dialog = page.getByRole("dialog", { name: "Create a new Bunch" });

    await expect(dialog).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Name" })).toBeVisible();
    await expect(
      page.getByRole("textbox", { name: "Description" }),
    ).toBeVisible();
    await expect(
      page.getByRole("switch", { name: "Private Bunch" }),
    ).toBeVisible();
    await expect(
      page.getByRole("switch", { name: "Private Bunch" }),
    ).not.toBeChecked();
    await expect(
      page.getByRole("button", { name: "Create Bunch" }),
    ).toBeVisible();
  });

  test("should validate bunch name when creating a bunch", async ({ page }) => {
    await page
      .getByRole("button", { name: /Create Bunch/i })
      .first()
      .click();
    await page.getByRole("button", { name: "Create Bunch" }).click();
    await expect(page.getByText("Name must be at least 3")).toBeVisible();
  });

  test("should navigate to bunch page when clicking on a bunch", async ({
    page,
  }) => {
    await page
      .getByRole("button", { name: /Create Bunch/i })
      .first()
      .click();
    const bunchName = `playwright-bunch-${Date.now()}`;
    await page.getByRole("textbox", { name: "Name" }).click();
    await page.getByRole("textbox", { name: "Name" }).fill(bunchName);

    await page.getByRole("textbox", { name: "Description" }).click();
    await page
      .getByRole("textbox", { name: "Description" })
      .fill("Test bunch for navigation");
    await page.getByRole("button", { name: "Create Bunch" }).click();
    await expect(
      page.getByText(/bunch.*created|created.*successfully/i),
    ).toBeVisible({ timeout: 5000 });

    const bunchLink = page.getByRole("link", { name: "pl" }).first();

    await expect(bunchLink).toBeVisible();
    await bunchLink.click();
    await expect(page).toHaveURL(/\/bunch\/.*/);
    await expect(
      page.getByRole("heading", { name: bunchName, exact: true }),
    ).toBeVisible();
    await expect(page.getByText("Test bunch for navigation")).toBeVisible();
  });
});
