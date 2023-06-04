module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  extends: [
    'standard'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: [
    '@typescript-eslint'
  ],
  ignorePatterns: [],
  rules: {
    "indent": ["error", 4],
    "no-undef": "off",
    "no-case-declarations": "off",
    "no-useless-constructor": "off",
    "new-cap": "off",
  }
}
