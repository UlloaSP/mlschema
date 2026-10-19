import assert from "node:assert/strict";
import { test } from "node:test";
import {
  createPythonRuntime,
  type RuntimeState,
  type WorkerLike,
} from "../../src/runtime/client.ts";
import type { FromWorker, ToWorker } from "../../src/runtime/protocol.ts";

const VERSIONS = { python: "3.14.2", pandas: "3.0.2", pydantic: "2.14.1", numpy: "2.4.6" };
const LIMITS = { bootMs: 40, runMs: 40 };

class FakeWorker implements WorkerLike {
  onmessage: WorkerLike["onmessage"] = null;
  onerror: WorkerLike["onerror"] = null;
  sent: ToWorker[] = [];
  terminated = false;
  failPost = false;
  postMessage(message: ToWorker) {
    if (this.failPost) throw new Error("could not clone message");
    this.sent.push(message);
  }
  terminate() {
    this.terminated = true;
  }
  emit(data: FromWorker) {
    this.onmessage?.({ data } as MessageEvent<FromWorker>);
  }
  crash(message: string) {
    this.onerror?.({ message, preventDefault() {} } as ErrorEvent);
  }
}

const setup = (limits = LIMITS) => {
  const workers: FakeWorker[] = [];
  const states: RuntimeState[] = [];
  const streams: string[] = [];
  const runtime = createPythonRuntime(
    () => {
      const worker = new FakeWorker();
      workers.push(worker);
      return worker;
    },
    { onState: (state) => states.push(state), onStream: (_, text) => streams.push(text) },
    limits,
  );
  const latest = () => workers.at(-1)!;
  return { runtime, workers, states, streams, latest };
};

const ready = () => {
  const context = setup();
  context.latest().emit({ type: "ready", versions: VERSIONS });
  return context;
};

test("boots, reports progress and becomes ready", () => {
  const { runtime, latest, states } = setup();
  latest().emit({ type: "progress", message: "Loading pandas…" });
  latest().emit({ type: "ready", versions: VERSIONS });
  assert.deepEqual(
    states.map((state) => state.status),
    ["booting", "booting", "ready"],
  );
  assert.deepEqual(runtime.state, { status: "ready", versions: VERSIONS });
  runtime.dispose();
});

test("runs code, forwards its streams and ignores stale run ids", async () => {
  const { runtime, latest, streams } = ready();
  const result = runtime.run("print(1)");
  assert.equal(runtime.state.status, "running");
  const { id } = latest().sent[0]!;
  latest().emit({ type: "stream", id: id + 1, stream: "stdout", text: "stale\n" });
  latest().emit({ type: "stream", id, stream: "stdout", text: "1\n" });
  latest().emit({ type: "done", id: id + 1, outcome: { kind: "none" }, durationMs: 1 });
  latest().emit({ type: "done", id, outcome: { kind: "json", text: "[]" }, durationMs: 3 });
  assert.deepEqual(await result, {
    kind: "finished",
    outcome: { kind: "json", text: "[]" },
    durationMs: 3,
  });
  assert.deepEqual(streams, ["1\n"]);
  assert.equal(runtime.state.status, "ready");
  runtime.dispose();
});

test("refuses to run before Python is ready", async () => {
  const { runtime, latest } = setup();
  assert.deepEqual(await runtime.run("1"), { kind: "unavailable" });
  assert.equal(latest().sent.length, 0);
  runtime.dispose();
});

test("a run past the time limit terminates the worker and boots a new one", async () => {
  const { runtime, workers } = ready();
  assert.deepEqual(await runtime.run("while True: pass"), { kind: "timeout", limitMs: 40 });
  assert.equal(workers[0]!.terminated, true);
  assert.equal(workers.length, 2);
  assert.equal(runtime.state.status, "booting");
  runtime.dispose();
});

test("cancel stops the run by restarting Python", async () => {
  const { runtime, workers } = ready();
  const result = runtime.run("while True: pass");
  runtime.cancel();
  assert.deepEqual(await result, { kind: "cancelled" });
  assert.equal(workers[0]!.terminated, true);
  assert.equal(workers.length, 2);
  runtime.cancel();
  assert.equal(workers.length, 2, "cancel without a run does nothing");
  runtime.dispose();
});

test("a worker crash during a run settles it as failed at once", async () => {
  const { runtime, workers, latest } = ready();
  const result = runtime.run("1");
  latest().crash("out of memory");
  const message = "Python stopped unexpectedly: out of memory";
  assert.deepEqual(await result, { kind: "failed", message });
  assert.deepEqual(runtime.state, { status: "failed", message });
  assert.equal(workers[0]!.terminated, true);
  await new Promise((resolve) => setTimeout(resolve, LIMITS.runMs * 2));
  assert.equal(workers.length, 1, "no restart until the visitor asks");
  runtime.restart();
  assert.equal(workers.length, 2);
  runtime.dispose();
});

test("boot errors and boot timeouts leave the runtime failed", async () => {
  const errored = setup();
  errored.latest().emit({ type: "boot-error", message: "network down" });
  assert.deepEqual(errored.runtime.state, {
    status: "failed",
    message: "Python could not start: network down",
  });
  const slow = setup();
  await new Promise((resolve) => setTimeout(resolve, LIMITS.bootMs * 2));
  assert.deepEqual(slow.runtime.state, {
    status: "failed",
    message: "Python could not start: no response within 0.04 seconds.",
  });
  assert.equal(slow.latest().terminated, true);
});

test("a worker that cannot be created or messaged fails explicitly", async () => {
  const runtime = createPythonRuntime(
    () => {
      throw new Error("Worker is not supported");
    },
    { onState() {}, onStream() {} },
    LIMITS,
  );
  assert.deepEqual(runtime.state, {
    status: "failed",
    message: "Python could not start: Worker is not supported",
  });
  assert.deepEqual(await runtime.run("1"), { kind: "unavailable" });

  const { runtime: posting, latest } = ready();
  latest().failPost = true;
  assert.deepEqual(await posting.run("1"), {
    kind: "failed",
    message: "Python stopped unexpectedly: could not clone message",
  });
  assert.equal(posting.state.status, "failed");
});
