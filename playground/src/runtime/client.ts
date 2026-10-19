import type { FromWorker, OutputStream, RunOutcome, RuntimeVersions, ToWorker } from "./protocol.ts";
import { BOOT_TIMEOUT_MS, RUN_TIMEOUT_MS } from "./versions.ts";

export interface WorkerLike {
  postMessage(message: ToWorker): void;
  terminate(): void;
  onmessage: ((event: MessageEvent<FromWorker>) => void) | null;
  onerror: ((event: ErrorEvent) => void) | null;
}

export type RuntimeState =
  | { status: "booting"; message: string }
  | { status: "ready"; versions: RuntimeVersions }
  | { status: "running"; versions: RuntimeVersions }
  | { status: "failed"; message: string };

export type RunResult =
  | { kind: "finished"; outcome: RunOutcome; durationMs: number }
  | { kind: "timeout"; limitMs: number }
  | { kind: "cancelled" }
  | { kind: "failed"; message: string }
  | { kind: "unavailable" };

export interface RuntimeListener {
  onState(state: RuntimeState): void;
  onStream(stream: OutputStream, text: string): void;
}

export interface RuntimeLimits {
  bootMs: number;
  runMs: number;
}

interface PendingRun {
  id: number;
  timer: ReturnType<typeof setTimeout>;
  resolve(result: RunResult): void;
}

const describe = (error: unknown) => (error instanceof Error ? error.message : String(error));

/**
 * Owns the Python worker. A run that times out or is cancelled terminates the
 * worker, which is the only way to stop arbitrary Python, and boots a fresh one.
 * A worker failure ends any pending run at once and leaves the runtime failed
 * until `restart()`.
 */
export const createPythonRuntime = (
  createWorker: () => WorkerLike,
  listener: RuntimeListener,
  limits: RuntimeLimits = { bootMs: BOOT_TIMEOUT_MS, runMs: RUN_TIMEOUT_MS },
) => {
  let worker: WorkerLike | undefined;
  let state: RuntimeState = { status: "booting", message: "Starting Python…" };
  let pending: PendingRun | undefined;
  let bootTimer: ReturnType<typeof setTimeout> | undefined;
  let nextId = 1;

  const setState = (next: RuntimeState) => {
    state = next;
    listener.onState(next);
  };
  const settle = (result: RunResult) => {
    if (!pending) return;
    clearTimeout(pending.timer);
    const { resolve } = pending;
    pending = undefined;
    if (result.kind === "finished" && state.status === "running") {
      setState({ status: "ready", versions: state.versions });
    }
    resolve(result);
  };
  const stopWorker = () => {
    clearTimeout(bootTimer);
    worker?.terminate();
    worker = undefined;
  };
  const fail = (reason: string) => {
    const message = `${state.status === "booting" ? "Python could not start" : "Python stopped unexpectedly"}: ${reason}`;
    stopWorker();
    settle({ kind: "failed", message });
    setState({ status: "failed", message });
  };

  const handle = (message: FromWorker) => {
    switch (message.type) {
      case "progress":
        if (state.status === "booting") setState({ status: "booting", message: message.message });
        return;
      case "ready":
        clearTimeout(bootTimer);
        setState({ status: "ready", versions: message.versions });
        return;
      case "boot-error":
        fail(message.message);
        return;
      case "stream":
        if (message.id === pending?.id) listener.onStream(message.stream, message.text);
        return;
      case "done":
        if (message.id === pending?.id) {
          settle({ kind: "finished", outcome: message.outcome, durationMs: message.durationMs });
        }
    }
  };

  const start = () => {
    stopWorker();
    setState({ status: "booting", message: "Starting Python…" });
    let current: WorkerLike;
    try {
      current = createWorker();
    } catch (error) {
      fail(describe(error));
      return;
    }
    worker = current;
    current.onmessage = ({ data }) => {
      if (worker === current) handle(data);
    };
    current.onerror = (event) => {
      if (worker !== current) return;
      event.preventDefault();
      fail(event.message || "the Python worker crashed.");
    };
    bootTimer = setTimeout(
      () => fail(`no response within ${limits.bootMs / 1000} seconds.`),
      limits.bootMs,
    );
  };

  const run = (code: string): Promise<RunResult> => {
    if (state.status !== "ready" || !worker) return Promise.resolve({ kind: "unavailable" });
    const id = nextId++;
    const target = worker;
    const result = new Promise<RunResult>((resolve) => {
      const timer = setTimeout(() => {
        settle({ kind: "timeout", limitMs: limits.runMs });
        start();
      }, limits.runMs);
      pending = { id, timer, resolve };
    });
    setState({ status: "running", versions: state.versions });
    try {
      target.postMessage({ type: "run", id, code });
    } catch (error) {
      fail(describe(error));
    }
    return result;
  };

  const restart = () => {
    settle({ kind: "cancelled" });
    start();
  };

  start();
  return {
    run,
    restart,
    /** Stops the current run, if any, by restarting Python. */
    cancel() {
      if (pending) restart();
    },
    get state() {
      return state;
    },
    dispose() {
      settle({ kind: "cancelled" });
      stopWorker();
    },
  };
};

export type PythonRuntime = ReturnType<typeof createPythonRuntime>;
