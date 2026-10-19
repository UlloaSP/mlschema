import type { RunResult } from "../runtime/client.ts";
import type { OutputStream } from "../runtime/protocol.ts";
import { icon, labelIcon } from "../icons.ts";
import { createJsonViewer } from "./viewer.ts";

const RESTART_HINT = "Check your connection, then choose Restart Python.";
const COPY_FEEDBACK_MS = 2000;

const MARKUP = `
  <button type="button" class="icon-button output-copy" data-role="copy" aria-label="Copy JSON" data-tooltip="Copy JSON" hidden>${icon("copy")}</button>
  <span class="visually-hidden" role="status" aria-live="polite" data-role="copy-status"></span>
  <pre class="output-error" data-role="error" role="alert" hidden></pre>
  <p class="output-note" data-role="note">Starting Python. The first visit downloads Python, pandas and pydantic; later visits use your browser cache.</p>
  <div class="output-json" data-role="json"></div>
  <pre class="output-repr" data-role="repr" tabindex="0" aria-label="Result repr" hidden></pre>
  <section class="output-console" data-role="console" aria-labelledby="console-title" hidden>
    <h3 id="console-title">Console</h3>
    <pre data-role="console-text" tabindex="0" aria-label="Console output"></pre>
  </section>
`;
export const createOutputPanel = (pane: HTMLElement) => {
  pane.innerHTML = MARKUP;
  const part = <T extends HTMLElement>(role: string) =>
    pane.querySelector<T>(`[data-role="${role}"]`)!;
  const copyStatus = part("copy-status");
  const copy = part<HTMLButtonElement>("copy");
  const error = part("error");
  const note = part("note");
  const jsonHost = part("json");
  const repr = part("repr");
  const consoleSection = part("console");
  const consoleText = part("console-text");
  const viewer = createJsonViewer(jsonHost);
  let bootFailed = false;
  // The startup note gives way to the first result, or to the ready runtime.
  let bootNote = true;
  let copyReset: ReturnType<typeof setTimeout> | undefined;

  const showNote = (text: string) => {
    bootNote = false;
    note.hidden = !text;
    note.textContent = text;
  };
  const showError = (text: string) => {
    error.hidden = !text;
    error.textContent = text;
  };
  const resetCopy = () => {
    clearTimeout(copyReset);
    labelIcon(copy, "copy", "Copy JSON");
    copyStatus.textContent = "";
  };
  const showJson = (text: string) => {
    viewer.show(text);
    // The copy action floats over the JSON, so it exists only while there is JSON to copy.
    copy.hidden = !text;
    resetCopy();
    jsonHost.hidden = false;
    repr.hidden = true;
  };
  const showFailure = (message: string) => {
    showError(`${message}\n${RESTART_HINT}`);
    bootFailed = true;
  };
  const clearResult = () => {
    showJson("");
    showError("");
    showNote("");
  };

  const copyJson = async () => {
    try {
      await navigator.clipboard.writeText(viewer.text());
      labelIcon(copy, "check", "Copy JSON", "Copied");
      copyStatus.textContent = "Copied to clipboard";
      copyReset = setTimeout(resetCopy, COPY_FEEDBACK_MS);
    } catch {
      labelIcon(copy, "error", "Copy JSON", "Copy unavailable");
      showNote("Copying is unavailable here; select the JSON instead.");
    }
  };
  copy.addEventListener("click", copyJson);

  return {
    begin() {
      consoleText.replaceChildren();
      consoleSection.hidden = true;
      pane.setAttribute("aria-busy", "true");
    },
    stream(stream: OutputStream, text: string) {
      const chunk = document.createElement("span");
      chunk.className = `console-${stream}`;
      chunk.textContent = text;
      consoleText.append(chunk);
      consoleSection.hidden = false;
    },
    finish(result: RunResult) {
      pane.setAttribute("aria-busy", "false");
      clearResult();
      if (result.kind === "timeout") {
        showError(
          `Stopped after ${result.limitMs / 1000} seconds. Python restarted, so variables and imports were reset.`,
        );
        return;
      }
      if (result.kind === "cancelled") {
        showNote("Run stopped. Python restarted, so variables and imports were reset.");
        return;
      }
      if (result.kind === "failed") {
        showFailure(result.message);
        return;
      }
      if (result.kind === "unavailable") {
        showNote("Python is not ready yet.");
        return;
      }
      const { outcome } = result;
      if (outcome.kind === "json") showJson(outcome.text);
      else if (outcome.kind === "error") showError(outcome.text);
      else if (outcome.kind === "none") {
        showNote("No result. End your code with an expression, such as infer_schema(df).");
      } else {
        showNote(`The last expression is a ${outcome.typeName}, not JSON. Showing its repr().`);
        jsonHost.hidden = true;
        repr.hidden = false;
        repr.textContent = outcome.text;
      }
    },
    /** A startup failure stays visible until Python boots again. */
    showFailure(message: string) {
      clearResult();
      showFailure(message);
    },
    showBooting() {
      if (!bootFailed) return;
      bootFailed = false;
      showError("");
      showNote("Restarting Python…");
      bootNote = true;
    },
    showReady() {
      if (bootNote) showNote("");
    },
  };
};
