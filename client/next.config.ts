import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // Enable standalone output for Docker
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_API_URL_V2: process.env.NEXT_PUBLIC_API_URL_V2 || 'http://localhost:8002',
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/:path*`,
      },
      {
        source: '/api/v2/:path*', 
        destination: `${process.env.NEXT_PUBLIC_API_URL_V2 || 'http://localhost:8002'}/:path*`,
      },
    ]
  },
};

export default nextConfig;
