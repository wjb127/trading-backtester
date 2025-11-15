export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Trading Backtest Platform</h1>
        <p className="text-lg text-gray-600 mb-8">
          주식/코인 트레이딩 전략 백테스팅 플랫폼
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/dashboard"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            대시보드
          </a>
          <a
            href="/strategies"
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            전략 관리
          </a>
          <a
            href="/backtests"
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            백테스팅
          </a>
        </div>
      </div>
    </main>
  )
}
