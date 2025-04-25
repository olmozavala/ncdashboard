import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

let commitHash = process.env.VITE_COMMIT_HASH || "dev";


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
