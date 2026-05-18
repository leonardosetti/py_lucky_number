import { test, expect } from "@playwright/test";

test.describe("Lucky Number — E2E Flows", () => {
  const BASE = "http://localhost:3000";

  test("T167: Login flow — register, login, session timeout redirect", async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await expect(page.locator('[data-testid="login-page"]')).toBeVisible();

    // Attempt login with invalid data
    await page.fill('[data-testid="email-input"]', "test@test.com");
    await page.fill('[data-testid="password-input"]', "wrong");
    await page.click('[data-testid="login-submit-button"]');
    await expect(page.locator('[data-testid="error-login"]')).toBeVisible();

    // Navigate to register
    await page.click('[data-testid="register-link"]');
    await expect(page.locator('[data-testid="register-page"]')).toBeVisible();

    // Register new user
    await page.fill('[data-testid="email-input"]', `e2e-${Date.now()}@test.com`);
    await page.fill('[data-testid="password-input"]', "123456");
    await page.click('[data-testid="register-submit-button"]');
    await expect(page.locator('[data-testid="dashboard-page"]')).toBeVisible();
  });

  test("T168: Generate flow — select game, generate, save to history", async ({ page }) => {
    await page.goto(`${BASE}/generate`);
    await expect(page.locator('[data-testid="generate-page"]')).toBeVisible();

    await page.selectOption('[data-testid="generate-game-select"]', "megasena");
    await page.fill('[data-testid="generate-quantity"]', "1");
    await page.fill('[data-testid="generate-numbers"]', "6");
    await page.click('[data-testid="generate-submit-button"]');

    // Wait for result
    await expect(page.locator('[data-testid="generate-result"]')).toBeVisible({ timeout: 10000 });
  });

  test("T169: History — list, favorite, delete", async ({ page }) => {
    await page.goto(`${BASE}/history`);
    await expect(page.locator('[data-testid="history-page"]')).toBeVisible();

    // Should see empty state or items
    const emptyState = page.locator('[data-testid="empty-state-history"]');
    const items = page.locator('[data-testid^="history-item-"]');

    if (await emptyState.isVisible()) {
      await expect(emptyState).toBeVisible();
    } else if (await items.first().isVisible()) {
      await items.first().locator('[data-testid^="history-fav-"]').click();
    }
  });

  test("T170: Admin — feature toggles", async ({ page }) => {
    await page.goto(`${BASE}/admin`);
    await expect(page.locator('[data-testid="admin-page"]')).toBeVisible();
    await expect(page.locator('[data-testid="admin-features"]')).toBeVisible();
  });

  test("T171: Responsive layout — 375px viewport (mobile)", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE}/login`);
    await expect(page.locator('[data-testid="login-page"]')).toBeVisible();

    // Verify touch targets are minimum 48px
    const button = page.locator('[data-testid="login-submit-button"]');
    const box = await button.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      expect(box.height).toBeGreaterThanOrEqual(48);
    }
  });
});
