/**
 * ESLint Flat Config for Next.js 16
 * Next.js 16 requires ESLint 9+ with flat config format
 *
 * @see https://nextjs.org/docs/app/api-reference/config/eslint
 * @see https://nextjs.org/docs/app/guides/upgrading/version-16
 * @see https://chris.lu/web_development/tutorials/next-js-16-linting-setup-eslint-9-flat-config
 */

import nextVitals from 'eslint-config-next/core-web-vitals';

const eslintConfig = [
  // Next.js core-web-vitals config (includes React, JSX-a11y, etc.)
  ...nextVitals,

  // Global ignores
  {
    ignores: [
      '.next/**',
      'out/**',
      'build/**',
      'dist/**',
      'node_modules/**',
      'next-env.d.ts',
      '*.config.js',
      '*.config.mjs',
    ],
  },

  // Custom rules overrides
  {
    rules: {
      '@next/next/no-html-link-for-pages': 'off',
      'react/no-unescaped-entities': 'off',
    },
  },
];

export default eslintConfig;
