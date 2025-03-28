import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { execSync } from "child_process";
const commitHash = execSync("git rev-parse --short HEAD").toString();

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
  },
  define: {
    "process.env": {
      VITE_COMMIT_HASH: commitHash,
    },
  },
});
