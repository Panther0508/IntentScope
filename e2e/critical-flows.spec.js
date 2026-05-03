import { test, expect } from '@playwright/test'

test.describe('Critical User Flows', () => {
  test('homepage loads correctly', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL('/')
    await expect(page.locator('h1')).toContainText('Real-time intention reading')
  })

  test('dashboard page loads and shows panels', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.locator('h2')).toContainText('Live Dashboard')
    // Check for sensor start button
    await expect(page.locator('button')).toContainText('Start Sensors')
  })

  test('navigation works', async ({ page }) => {
    await page.goto('/')
    // Navigate to Dashboard
    await page.click('a[href="/dashboard"]')
    await expect(page).toHaveURL('/dashboard')
    // Navigate to Analysis
    await page.click('a[href="/analysis"]')
    await expect(page).toHaveURL('/analysis')
    // Navigate to RobotLab
    await page.click('a[href="/robot"]')
    await expect(page).toHaveURL('/robot')
  })

  test('settings page loads with wired controls', async ({ page }) => {
    await page.goto('/settings')
    await expect(page.locator('h2')).toContainText('Settings')
    // Check for cache size display (starts at 0 KB)
    await expect(page.locator('.text-muted')).toContainText('0 KB')
    // Check for toggle
    await expect(page.locator('input[type="checkbox"]')).toBeChecked()
  })

  test('about page renders', async ({ page }) => {
    await page.goto('/about')
    await expect(page.locator('h2')).toContainText('About')
  })
})
