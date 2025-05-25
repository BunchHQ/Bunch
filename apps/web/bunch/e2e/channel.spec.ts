import { expect, test } from "@playwright/test";

test.describe("Channel Management", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");

    await page
      .getByRole("button", { name: /Create Bunch/i })
      .first()
      .click();
    await page.getByRole("textbox", { name: "Name" }).click();
    await page
      .getByRole("textbox", { name: "Name" })
      .fill("Playwright Test Bunch");

    await page.getByRole("textbox", { name: "Description" }).click();
    await page
      .getByRole("textbox", { name: "Description" })
      .fill("A test bunch for channels");
    await page.getByRole("button", { name: "Create Bunch" }).click();

    const bunchLink = page.getByRole("link", { name: "Pl" }).first();

    await expect(bunchLink).toBeVisible();
    await bunchLink.click();
  });

  test("should create a new text channel", async ({ page }) => {
    await page.getByRole("button", { name: "Create a channel" }).click();

    await page.getByRole("combobox").click();
    await page.getByRole("option", { name: "Text Channel" }).click();
    await page.getByRole("textbox", { name: "Channel Name" }).click();
    await page
      .getByRole("textbox", { name: "Channel Name" })
      .fill("Test Channel");
    await page.getByRole("textbox", { name: "Description (Optional)" }).click();
    await page
      .getByRole("textbox", { name: "Description (Optional)" })
      .fill("A test channel");
    await page.getByRole("button", { name: "Create Channel" }).click();

    await expect(page.getByText("Success", { exact: true })).toBeVisible();
    await expect(page.getByText("Channel created successfully!")).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Test Channel" }),
    ).toBeVisible();
  });

  test("should send and display messages in channel", async ({ page }) => {
    await page.getByRole("button", { name: "Create a channel" }).click();
    await page.getByRole("combobox").click();
    await page.getByRole("option", { name: "Text Channel" }).click();
    await page.getByRole("textbox", { name: "Channel Name" }).click();
    await page
      .getByRole("textbox", { name: "Channel Name" })
      .fill("Chat Channel");
    await page.getByRole("button", { name: "Create Channel" }).click();

    await page.getByRole("link", { name: "Chat Channel" }).click();

    const messageInput = page.getByRole("textbox", { name: /Message #/ });
    await messageInput.click();
    await messageInput.fill("Hello there!");
    await page.locator(".border-t > div > button:nth-child(3)").click();

    await expect(page.getByText("Hello there!")).toBeVisible();
  });

  test("should show empty state for new channel", async ({ page }) => {
    await page.getByRole("button", { name: "Create a channel" }).click();
    await page.getByRole("combobox").click();
    await page.getByRole("option", { name: "Text Channel" }).click();
    await page.getByRole("textbox", { name: "Channel Name" }).click();
    await page
      .getByRole("textbox", { name: "Channel Name" })
      .fill("Empty Channel");
    await page.getByRole("button", { name: "Create Channel" }).click();

    await page.getByRole("link", { name: "Empty Channel" }).click();

    await expect(
      page.getByRole("heading", { name: "No messages yet" }),
    ).toBeVisible();
  });
});
