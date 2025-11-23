/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone', // For Docker deployments
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig
