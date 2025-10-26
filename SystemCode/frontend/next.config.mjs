/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // 注意这里去掉一个 /api/
        destination: 'https://irrsbackend-234550193243.asia-southeast1.run.app/:path*',
      },
    ];
  },

  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
