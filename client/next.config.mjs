/** @type {import('next').NextConfig} */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "/verify";

const nextConfig = {
  // Set NEXT_PUBLIC_BASE_PATH="" when migrating to a dedicated domain
  basePath: basePath === "" ? undefined : basePath,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://pivs-server:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
