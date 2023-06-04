export default {
    // see https://stackoverflow.com/questions/42260218/jest-setup-syntaxerror-unexpected-token-export
    moduleNameMapper: {
        "^lodash-es$": "lodash"
    },
    maxWorkers: 1,
    preset: "ts-jest",
    reporters: ["./test/custom_reporter.js"],
    setupFiles: ["./test/setup.ts"],
    verbose: false,
}