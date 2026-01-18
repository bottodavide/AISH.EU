/**
 * Next.js 16 Configuration
 * @type {import('next').NextConfig}
 * @see https://nextjs.org/docs/app/api-reference/next-config-js
 * @see https://nextjs.org/docs/app/guides/upgrading/version-16
 */
const nextConfig = {
  /* Environment */
  reactStrictMode: true,
  poweredByHeader: false,

  /* Build Configuration */
  // NOTE: eslint config removed (no longer supported in Next.js 16)
  // Run `npm run lint` separately to check for errors
  typescript: {
    ignoreBuildErrors: true,
  },

  /* Image Optimization */
  images: {
    // Updated from deprecated 'domains' to 'remotePatterns'
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'https',
        hostname: 'aistrategyhub.eu',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  /* Internationalization (future) */
  // i18n: {
  //   locales: ['it', 'en'],
  //   defaultLocale: 'it',
  // },

  /* Headers */
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  /* Rewrites (optional - se backend su path diverso) */
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: 'http://localhost:8000/api/:path*',
  //     },
  //   ];
  // },

  /* Turbopack Configuration (Next.js 16 default bundler) */
  // Empty config to silence webpack migration warning
  // Turbopack is now the default - no custom config needed
  turbopack: {},

  /* Output */
  output: 'standalone', // Per Docker optimization

  /* Experimental Features */
  experimental: {
    // serverActions: true,
  },
};

module.exports = nextConfig;
