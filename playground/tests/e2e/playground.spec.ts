import { expect, test, type FrameLocator, type Page } from "@playwright/test";

// The workspace runs inside the editor frame; the page around it owns the header and menu.
const frame = (page: Page) => page.frameLocator('iframe[title="Python editor"]');
const editor = (ws: FrameLocator) => ws.getByRole("textbox", { name: "Python code" });
const schema = (ws: FrameLocator) => ws.getByRole("textbox", { name: "Schema JSON" });
const runButton = (ws: FrameLocator) => ws.getByRole("button", { name: /^(Run|Stop)$/ });
const status = (ws: FrameLocator, text: string) => ws.getByRole("status").filter({ hasText: text });
const tooltip = (target: ReturnType<FrameLocator["getByRole"]>) =>
  target.evaluate((element) => {
    const style = getComputedStyle(element, "::after");
    return { text: style.content, opacity: style.opacity };
  });

const replaceCode = async (page: Page, code: string) => {
  await editor(frame(page)).click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.press("Delete");
  // insertText keeps indentation exactly; typing would trigger auto-indent.
  await page.keyboard.insertText(code);
};

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

test("runs the first example with real MLschema and shows JSON and console", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind": "date"');
  await expect(schema(ws)).toContainText('"mappedTo": "joined"');
  await expect(status(ws, "Done")).toBeAttached();
  await expect(ws.getByRole("region", { name: "Console" })).toContainText("datetime64");
  await expect(ws.getByRole("button", { name: "Copy JSON" })).toBeVisible();
  // Simplified chrome: no runtime notice, badge, result heading or credit.
  for (const text of ["Experimental runtime", "Ran in", "by eshkra"]) {
    await expect(page.getByText(text)).toHaveCount(0);
    await expect(ws.getByText(text)).toHaveCount(0);
  }
  await expect(ws.getByRole("heading", { name: "Schema JSON" })).toHaveCount(0);
  await expect(page.getByText("Playground", { exact: true })).toHaveCount(0);
  // The product name is always written MLschema.
  await expect(page).toHaveTitle("MLschema Playground");
  await expect(page.getByRole("link", { name: "MLschema home" })).toHaveText("MLschema");
  await expect(page.getByRole("navigation", { name: "MLschema resources" })).toBeVisible();
});

test("icon controls keep accessible names and show labels on hover and focus", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  const reset = ws.getByRole("button", { name: "Reset example" });
  await expect(reset).toHaveText("");
  await expect(ws.getByRole("button", { name: "Restart Python" })).toHaveText("");
  await expect(runButton(ws)).toHaveAccessibleName("Run");
  await expect(ws.getByRole("status").filter({ hasText: "Done" })).toHaveAttribute("data-tooltip", "Done");
  expect(await tooltip(reset)).toEqual({ text: '"Reset example"', opacity: "0" });
  await reset.focus();
  await page.keyboard.press("Shift+Tab");
  await page.keyboard.press("Tab");
  await expect.poll(() => tooltip(reset)).toEqual({ text: '"Reset example"', opacity: "1" });
  const docs = page.getByRole("link", { name: "Docs" });
  await expect(docs).toHaveAttribute("href", "https://docs.mlschema.eshkra.dev/");
  await expect(page.getByRole("link", { name: "GitHub" })).toBeVisible();
  await expect(page.getByRole("link", { name: "eshkra" })).toHaveAttribute("href", "https://eshkra.dev/");
  if (!test.info().project.name.startsWith("mobile")) {
    await docs.hover();
    await expect.poll(() => tooltip(docs)).toEqual({ text: '"Docs"', opacity: "1" });
  }
});

test("copy reports success and failure", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  const copy = ws.getByRole("button", { name: "Copy JSON" });
  await copy.click();
  await expect(copy).toHaveAttribute("data-tooltip", "Copied");
  await expect(ws.getByText("Copied to clipboard")).toBeAttached();
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied).toContain('"mappedTo": "joined"');
  await expect(copy).toHaveAttribute("data-tooltip", "Copy JSON");
  await copy.evaluate((element) => {
    const clipboard = element.ownerDocument.defaultView!.navigator.clipboard;
    clipboard.writeText = () => Promise.reject(new Error("NotAllowedError"));
  });
  await copy.click();
  await expect(copy).toHaveAttribute("data-tooltip", "Copy unavailable");
  await expect(ws.getByText("Copying is unavailable here; select the JSON instead.")).toBeVisible();
});

test("shows Python tracebacks, hides copy and keeps the editor usable", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  await replaceCode(page, "import pandas as pd\nfrom mlschema import infer_schema\ninfer_schema(pd.DataFrame())\n");
  await page.keyboard.press("ControlOrMeta+Enter");
  const alert = ws.getByRole("alert");
  await expect(alert).toContainText('File "<playground>", line 3');
  await expect(alert).toContainText("EmptyDataFrameError");
  await expect(schema(ws)).toHaveText("");
  await expect(ws.getByRole("button", { name: "Copy JSON" })).toBeHidden();
  await expect(status(ws, "Error")).toBeAttached();
});

test("stop interrupts a runaway loop and Python restarts", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  await replaceCode(page, "while True:\n    pass\n");
  await runButton(ws).click();
  await expect(runButton(ws)).toHaveAccessibleName("Stop");
  await expect(status(ws, "Running")).toBeAttached();
  await expect(ws.getByRole("combobox", { name: "Example" })).toBeDisabled();
  await runButton(ws).click();
  await expect(ws.getByText("Run stopped. Python restarted")).toBeVisible();
  await expect(status(ws, "Ready")).toBeAttached();
  await replaceCode(page, "[1, 2]\n");
  await runButton(ws).click();
  await expect(schema(ws)).toContainText("2");
  await expect(status(ws, "Done")).toBeAttached();
});

test("restart Python reboots the runtime and runs again", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  await ws.getByRole("button", { name: "Restart Python" }).click();
  await expect(status(ws, "Ready")).toBeAttached();
  await runButton(ws).click();
  await expect(status(ws, "Done")).toBeAttached();
  await expect(schema(ws)).toContainText('"kind": "date"');
});

test("examples switch, persist and reset", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  await ws.getByRole("combobox", { name: "Example" }).selectOption("positional");
  await expect(schema(ws)).toContainText('"mappedTo": 0');
  await page.reload();
  await expect(ws.getByRole("combobox", { name: "Example" })).toHaveValue("positional");
  await expect(editor(ws)).toContainText("with_positional_mappings");
  await replaceCode(page, "None\n");
  await ws.getByRole("button", { name: "Reset example" }).click();
  await expect(editor(ws)).toContainText("with_positional_mappings");
});

test("layout fits the viewport without page scrolling", async ({ page }) => {
  const ws = frame(page);
  await expect(schema(ws)).toContainText('"kind"');
  const overflow = (root: HTMLElement) => ({
    x: root.scrollWidth - root.clientWidth,
    y: root.scrollHeight - root.clientHeight,
  });
  expect(await page.locator("html").evaluate(overflow)).toEqual({ x: 0, y: 0 });
  expect(await ws.locator("html").evaluate(overflow)).toEqual({ x: 0, y: 0 });
});
