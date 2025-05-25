import { expect, test } from "@playwright/test";

test.describe("Navigation", () => {
  test("should navigate between key pages correctly", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Browse Bunches" }).click();
    await expect(page).toHaveURL(/\/browse$/);

    const homeLink = page.getByRole("link", { name: /home/i });
    if (await homeLink.isVisible()) {
      await homeLink.click();
      await expect(page).toHaveURL(/\/$/);
    } else {
      await page.goto("/");
    }

    await page.getByRole("button", { name: "Create Bunch" }).first().click();
    const createDialog = page.getByRole("dialog");
    const createDialogTitle = createDialog.getByText(/Create a new Bunch/i);
    await expect(createDialog).toBeVisible();
    await expect(createDialogTitle).toBeVisible();

    // await page.getByRole("button", { name: "Join Bunch" }).click();
    // const joinDialog = page.getByRole("dialog");
    // const joinDialogTitle = joinDialog.getByText(/Join a private Bunch/i);
    // await expect(joinDialog).toBeVisible();
    // await expect(joinDialogTitle).toBeVisible();
  });

  test("should have functioning sidebar navigation", async ({ page }) => {
    await page.goto("/");

    const sidebar = page.getByRole("navigation");
    await sidebar.isVisible();

    const collapseButton = page.getByRole("button", {
      name: /Toggle Sidebar/i,
    });

    if (await collapseButton.isVisible()) {
      const sidebarBefore = await sidebar.boundingBox();

      await collapseButton.click();

      await page.waitForTimeout(500);

      const sidebarAfter = await sidebar.boundingBox();

      if (sidebarBefore && sidebarAfter) {
        expect(sidebarBefore.width).not.toBe(sidebarAfter.width);
      }

      await collapseButton.click();
    }
  });

  // TODO: Make this test really work. After implementing the settings page
  test("should navigate to user settings", async ({ page }) => {
    await page.goto("/");

    const userMenu = page.getByRole("button", {
      name: /user|profile|account/i,
    });

    if (await userMenu.isVisible()) {
      await userMenu.click();

      const settingsLink = page.getByRole("menuitem", {
        name: /settings|profile|account/i,
      });

      if (await settingsLink.isVisible()) {
        await settingsLink.click();

        await expect(page).toHaveURL(/\/(settings|profile|account)/);

        const settingsHeading = page.getByRole("heading", {
          name: /settings|profile|account/i,
        });
        await expect(settingsHeading).toBeVisible();
      }
    }
  });

  test("should use browser back/forward navigation correctly", async ({
    page,
  }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Browse Bunches" }).click();
    await expect(page).toHaveURL(/\/browse$/);

    await page.goBack();
    await expect(page).toHaveURL(/\/$/);

    await page.goForward();
    await expect(page).toHaveURL(/\/browse$/);
  });
});
