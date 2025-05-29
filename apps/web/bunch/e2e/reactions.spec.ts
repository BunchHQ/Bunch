import { expect, test } from "@playwright/test";

test.describe("Message Reactions", () => {
  let bunchName: string;
  let channelName: string;
  let bunchAbbrev: string;

  test.beforeEach(async ({ page }) => {
    // Generate unique names to avoid conflicts
    const timestamp = Date.now();
    bunchName = `Reactions Test ${timestamp}`;
    channelName = `reaction-tests-${timestamp}`;
    bunchAbbrev = bunchName.slice(0, 2);

    await page.goto("/");

    // Create a test bunch
    await page
      .getByRole("button", { name: /Create Bunch/i })
      .first()
      .click();
    await page.getByRole("textbox", { name: "Name" }).click();
    await page.getByRole("textbox", { name: "Name" }).fill(bunchName);

    await page.getByRole("textbox", { name: "Description" }).click();
    await page
      .getByRole("textbox", { name: "Description" })
      .fill("Testing message reactions");
    await page.getByRole("button", { name: "Create Bunch" }).click(); // Wait for success message and navigate to the bunch
    await expect(page.getByText("Success", { exact: true })).toBeVisible();
    const bunchLink = page.getByRole("link", { name: bunchAbbrev }).first();
    await expect(bunchLink).toBeVisible();
    await bunchLink.click();

    // Create a test channel
    await page.getByRole("button", { name: "Create New Channel" }).click();
    await page.getByRole("combobox").click();
    await page.getByRole("option", { name: "Text Channel" }).click();
    await page.getByRole("textbox", { name: "Channel Name" }).click();
    await page.getByRole("textbox", { name: "Channel Name" }).fill(channelName);
    await page.getByRole("button", { name: "Create Channel" }).click();

    // Wait for success message and navigate to the channel
    await expect(page.getByText("Success", { exact: true })).toBeVisible();
    await page.getByRole("link", { name: channelName }).click();

    // Send a test message
    const messageInput = page.getByRole("textbox", { name: /Message #/ });
    await messageInput.click();
    await messageInput.fill("Test message for reactions! 🎉");
    await page.keyboard.press("Enter");

    // Wait for message to appear
    await expect(
      page.getByText("Test message for reactions! 🎉").first()
    ).toBeVisible();
  });
  test("should show emoji picker when hovering over message", async ({
    page,
  }) => {
    // Hover over the message to reveal reaction button
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();

    await messageContainer.hover();

    // Check that the emoji picker button appears - scope within message container
    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );

    await expect(emojiPickerButton).toBeVisible();
  });
  test("should open emoji picker when clicking plus button", async ({
    page,
  }) => {
    // Hover over message to show reaction controls
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();

    await messageContainer.hover();

    // Click the emoji picker button - scope within message container
    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );
    await expect(emojiPickerButton).toBeVisible();
    await emojiPickerButton.click();

    // Verify emoji picker is open with available emojis
    await expect(page.getByTestId("emoji-picker-content")).toBeVisible();
    await expect(page.getByText("👍")).toBeVisible();
    await expect(page.getByText("❤️")).toBeVisible();
    await expect(page.getByText("😂")).toBeVisible();
    await expect(page.getByText("😮")).toBeVisible();
    await expect(page.getByText("😢")).toBeVisible();
    await expect(page.getByText("😡")).toBeVisible();
  });
  test("should add reaction when clicking emoji in picker", async ({
    page,
  }) => {
    // Hover over message and open emoji picker
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();
    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );
    await emojiPickerButton.click();

    // Click on thumbs up emoji
    await page.getByText("👍").click();

    // Verify reaction appears on the message
    const reactionButton = messageContainer.getByRole("button").filter({
      hasText: "👍",
    });

    await expect(reactionButton).toBeVisible();
    await expect(reactionButton).toContainText("1");
  });
  test("should remove reaction when clicking existing reaction", async ({
    page,
  }) => {
    // First add a reaction
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();
    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );
    await emojiPickerButton.click();
    await page.getByText("❤️").click();

    // Verify reaction was added
    const reactionButton = messageContainer.getByRole("button").filter({
      hasText: "❤️",
    });

    await expect(reactionButton).toBeVisible();
    await expect(reactionButton).toContainText("1");

    // Click the reaction to remove it
    await reactionButton.click();

    // Verify reaction is removed (button should no longer be visible)
    await expect(reactionButton).not.toBeVisible();
  });
  test("should show different visual state for user's own reactions", async ({
    page,
  }) => {
    // Add a reaction
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();
    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );
    await emojiPickerButton.click();
    await page.getByText("😂").click();

    // Check that user's own reaction has different styling (highlighted)
    const reactionButton = messageContainer.getByRole("button").filter({
      hasText: "😂",
    });

    await expect(reactionButton).toBeVisible();
    await expect(reactionButton).toHaveClass(/bg-blue-100/);
  });
  test("should show reaction counts correctly", async ({ page }) => {
    // Add multiple different reactions
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();
    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );

    // Add thumbs up
    await emojiPickerButton.click();
    await page.getByText("👍").click();

    // Add heart
    await messageContainer.hover();
    await emojiPickerButton.click();
    await page.getByText("❤️").click();

    // Add another thumbs up (should not work - same user, same emoji)
    await messageContainer.hover();
    await emojiPickerButton.click();
    await page.getByText("👍").click();

    // Verify counts
    const thumbsUpButton = messageContainer.getByRole("button").filter({
      hasText: "👍",
    });
    const heartButton = messageContainer.getByRole("button").filter({
      hasText: "❤️",
    });

    await expect(thumbsUpButton).toContainText("1"); // Should still be 1
    await expect(heartButton).toContainText("1");
  });
  test("should show tooltip with user information on hover", async ({
    page,
  }) => {
    // Add a reaction
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();
    await messageContainer.hover();
    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );

    await emojiPickerButton.click();
    await page.getByText("🔥").click();

    // Hover over the reaction button
    const reactionButton = messageContainer.getByRole("button").filter({
      hasText: "🔥",
    });

    await reactionButton.hover(); // Check for tooltip content (this might vary based on your tooltip implementation)
    // The tooltip should show the username who reacted
    await expect(page.locator("[role='tooltip']")).toBeVisible();
  });
  test("should toggle reaction correctly with multiple clicks", async ({
    page,
  }) => {
    // Add and remove reaction multiple times
    const messageContainer = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .first();

    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );

    // Add reaction
    await emojiPickerButton.click();
    await page.getByText("😮").click();

    let reactionButton = messageContainer.getByRole("button").filter({
      hasText: "😮",
    });

    await expect(reactionButton).toBeVisible();

    // Remove reaction
    await reactionButton.click();
    await expect(reactionButton).not.toBeVisible();

    // Add reaction again
    await messageContainer.hover();
    await emojiPickerButton.click();
    await page.getByText("😮").click();

    reactionButton = messageContainer.getByRole("button").filter({
      hasText: "😮",
    });

    await expect(reactionButton).toBeVisible();
    await expect(reactionButton).toContainText("1");
  });
  test("should handle multiple messages with reactions independently", async ({
    page,
  }) => {
    // Send another message
    const messageInput = page.getByRole("textbox", { name: /Message #/ });
    await messageInput.click();
    await messageInput.fill("Second test message! 🚀");
    await page.keyboard.press("Enter");

    await expect(page.getByText("Second test message! 🚀")).toBeVisible();

    // Add reaction to first message
    const firstMessage = page.locator(".group").filter({
      hasText: "Test message for reactions! 🎉",
    });
    await firstMessage.hover();

    let emojiPickerButton = firstMessage.getByTestId(
      "message-emoji-picker-trigger"
    );
    await emojiPickerButton.click();
    await page.getByText("👍").click();

    // Add different reaction to second message
    const secondMessage = page.locator(".group").filter({
      hasText: "Second test message! 🚀",
    });
    await secondMessage.hover();

    emojiPickerButton = secondMessage.getByTestId(
      "message-emoji-picker-trigger"
    );

    await emojiPickerButton.click();
    await page.getByText("❤️").click();

    // Verify reactions are on correct messages
    const firstReaction = firstMessage.getByRole("button").filter({
      hasText: "👍",
    });
    const secondReaction = secondMessage.getByRole("button").filter({
      hasText: "❤️",
    });

    await expect(firstReaction).toBeVisible();
    await expect(secondReaction).toBeVisible();

    // Verify reactions are NOT on wrong messages
    await expect(
      firstMessage.getByRole("button").filter({
        hasText: "❤️",
      })
    ).not.toBeVisible();

    await expect(
      secondMessage.getByRole("button").filter({
        hasText: "👍",
      })
    ).not.toBeVisible();
  });
  test("should close emoji picker when clicking outside", async ({ page }) => {
    // Open emoji picker
    const messageContainer = page.locator(".group").filter({
      hasText: "Test message for reactions! 🎉",
    });
    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );

    await emojiPickerButton.click();

    // Verify picker is open
    await expect(page.getByTestId("emoji-picker-content")).toBeVisible();
    await expect(page.getByText("👍")).toBeVisible();

    // Click outside the picker
    await page.click("body", { position: { x: 100, y: 100 } });

    // Verify picker is closed
    await expect(page.getByTestId("emoji-picker-content")).not.toBeVisible();
    await expect(page.getByText("👍")).not.toBeVisible();
  });
  test("should persist reactions after page reload", async ({ page }) => {
    // Add a reaction
    const messageContainer = page.locator(".group").filter({
      hasText: "Test message for reactions! 🎉",
    });
    await messageContainer.hover();

    const emojiPickerButton = messageContainer.getByTestId(
      "message-emoji-picker-trigger"
    );

    await emojiPickerButton.click();
    await page.getByText("🎉").click();

    // Verify reaction is added
    const reactionButton = messageContainer.getByRole("button").filter({
      hasText: "🎉",
    });

    await expect(reactionButton).toBeVisible();

    // Reload the page
    await page.reload();

    // Wait for content to load
    await expect(
      page.getByText("Test message for reactions! 🎉")
    ).toBeVisible();

    // Verify reaction is still there
    const persistedReaction = page
      .locator(".group")
      .filter({
        hasText: "Test message for reactions! 🎉",
      })
      .getByRole("button")
      .filter({
        hasText: "🎉",
      });

    await expect(persistedReaction).toBeVisible();
    await expect(persistedReaction).toContainText("1");
  });
});
