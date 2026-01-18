/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  /* Environment */
  reactStrictMode: true,
  poweredByHeader: false,

  /* Build Configuration */
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },

  /* Image Optimization */
  images: {
    domains: [
      'localhost',
      'aistrategyhub.eu',
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

  /* Webpack Configuration */
  webpack: (config, { isServer }) => {
    // Custom webpack config se necessario
    return config;
  },

  /* Output */
  output: 'standalone', // Per Docker optimization

  /* Experimental Features */
  experimental: {
    // serverActions: true,
  },
};

module.exports = nextConfig;
