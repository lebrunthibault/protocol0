import { defineConfig } from "vite";

export default defineConfig({
    root:  "./com.thibault.p0.sdPlugin",
    build: {
        outDir: "./public",
        lib: {
            name: "p0",
            entry: "app.ts",
            formats: ["iife"],
            fileName: "bundle"
        },
        minify: false
    }
});