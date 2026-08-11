import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // React Compiler (stable in Next 16) — auto-memoizes components.
  // Requires the `babel-plugin-react-compiler` dev dependency.
  reactCompiler: true,

  // Allow <Image> to load media served by the backend (dev: Django/MinIO).
  // Add your production media host here before deploying.
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000" },
      { protocol: "http", hostname: "localhost", port: "9000" },
    ],
  },
};

export default nextConfig;
