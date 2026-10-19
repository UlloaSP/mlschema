import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { fileURLToPath } from "node:url";
import { sidebar } from "./src/navigation";

const repo = (path: string) =>
  fileURLToPath(new URL(`../${path}`, import.meta.url)).replaceAll("\\", "/");

export default defineConfig({
  site: "https://docs.mlschema.eshkra.dev",
  trailingSlash: "always",
  devToolbar: { enabled: false },
  vite: {
    // The docs read the shared brand assets at the repository root.
    server: {
      fs: {
        allow: [fileURLToPath(new URL(".", import.meta.url)), repo("brand")],
      },
    },
  },
  integrations: [
    starlight({
      title: "MLschema",
      description: "Validated, frontend-ready field schemas inferred from pandas DataFrames.",
      components: {
        Head: "./src/components/BrandHead.astro",
        SiteTitle: "./src/components/BrandTitle.astro",
        SocialIcons: "./src/components/SocialIcons.astro",
        Footer: "./src/components/Footer.astro",
      },
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/UlloaSP/mlschema",
        },
      ],
      editLink: {
        baseUrl: "https://github.com/UlloaSP/mlschema/edit/main/docs/",
      },
      expressiveCode: {
        // The landing's code themes, switched with the documentation theme.
        themes: ["github-dark-default", "github-light-default"],
        styleOverrides: {
          borderRadius: "12px",
          borderColor: "var(--ms-border)",
          codeFontFamily: "var(--brand-font-mono)",
          uiFontFamily: "var(--brand-font-sans)",
          codeFontSize: "0.8125rem",
          codeLineHeight: "1.7",
          frames: {
            shadowColor: "transparent",
            editorTabBarBackground: "var(--ms-subtle)",
            editorActiveTabBackground: "var(--ms-code-bg)",
            editorActiveTabIndicatorTopColor: "var(--ms-ember)",
            editorActiveTabIndicatorBottomColor: "transparent",
            editorBackground: "var(--ms-code-bg)",
            terminalTitlebarBackground: "var(--ms-subtle)",
            terminalBackground: "var(--ms-code-bg)",
          },
        },
      },
      customCss: [
        "./src/styles/typography.css",
        "./src/styles/theme.css",
        "./src/styles/content.css",
        "./src/styles/home.css",
      ],
      sidebar,
    }),
  ],
});
