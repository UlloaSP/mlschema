import { fileURLToPath } from "node:url";
import { defineConfig } from "vite-plus";

const repoRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  // The worker bundles ../src/mlschema and the header uses ../brand.
  server: { fs: { allow: [repoRoot] } },
  worker: { format: "es" },
  build: { target: "es2022" },
});
