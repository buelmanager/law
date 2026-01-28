/** @type {import('next').NextConfig} */
const nextConfig = {
  // 정적 빌드 (FastAPI에서 서빙하기 위해)
  output: 'export',
  
  // 이미지 최적화 비활성화 (정적 빌드에서 필요)
  images: {
    unoptimized: true,
  },

  // 기본 경로 설정 (필요시)
  basePath: '',
  assetPrefix: '',

  // React 엄격 모드 활성화
  reactStrictMode: true,
}

module.exports = nextConfig
