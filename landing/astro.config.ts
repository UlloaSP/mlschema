import { fileURLToPath } from "node:url";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://mlschema.eshkra.dev",
  trailingSlash: "always",
  devToolbar: { enabled: false },
  vite: {
    // The dev server must read the shared brand mark outside this package.
    server: {
      fs: {
        allow: [
          fileURLToPath(new URL(".", import.meta.url)),
          fileURLToPath(new URL("../brand", import.meta.url)),
        ],
      },
    },
  },
});
