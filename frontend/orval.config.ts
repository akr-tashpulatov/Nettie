import { defineConfig } from "orval";
import { loadEnvConfig } from "@next/env";

loadEnvConfig(process.cwd());

const input = {
  target: process.env.OPENAPI_URL as string,
  override: { transformer: "./src/shared/api/orval/transformer.mjs" },
  filters: { mode: "exclude" as const, tags: ["Health", "Metrics", "Webhook"] },
};

export default defineConfig({
  api: {
    input,
    output: {
      mode: "tags-split",
      client: "react-query",
      httpClient: "axios",
      namingConvention: "kebab-case",
      target: "./src/shared/api/generated",
      schemas: "./src/shared/api/generated/model",
      clean: true,
      formatter: "prettier",
      override: {
        mutator: {
          path: "./src/shared/api/api-instance.ts",
          name: "createInstance",
        },
        query: {
          signal: true,
          shouldExportQueryKey: true,
        },
      },
    },
  },
  zod: {
    input,
    output: {
      client: "zod",
      mode: "tags-split",
      override: {
        zod: {
          version: 4,
          variant: 'classic'
        }
      },
      formatter: "prettier",
      fileExtension: ".schema.ts",
      namingConvention: "kebab-case",
      target: "./src/shared/api/generated",
    },
  },
});
