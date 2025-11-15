import Link from 'next/link'

export default function Strategies() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="text-xl font-bold text-gray-900">
              Trading Backtest
            </Link>
            <div className="flex space-x-4">
              <Link
                href="/dashboard"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md"
              >
                대시보드
              </Link>
              <Link
                href="/strategies"
                className="text-blue-600 font-medium px-3 py-2 rounded-md"
              >
                전략 관리
              </Link>
              <Link
                href="/backtests"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md"
              >
                백테스팅
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">전략 관리</h1>
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
              + 새 전략 만들기
            </button>
          </div>

          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                내 전략 목록
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                생성된 트레이딩 전략을 관리하고 백테스팅을 실행하세요
              </p>
            </div>

            <div className="px-4 py-5 sm:p-6">
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  아직 생성된 전략이 없습니다
                </h3>
                <p className="text-gray-500 mb-6">
                  첫 번째 트레이딩 전략을 만들어보세요
                </p>
                <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                  전략 만들기
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                전략 예시
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                참고할 수 있는 기본 전략 템플릿
              </p>
            </div>
            <div className="border-t border-gray-200">
              <ul className="divide-y divide-gray-200">
                <li className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">
                        이동평균 크로스오버 (MA Crossover)
                      </h4>
                      <p className="mt-1 text-sm text-gray-500">
                        단기 이동평균이 장기 이동평균을 상향 돌파할 때 매수, 하향 돌파할 때 매도
                      </p>
                    </div>
                    <button className="ml-4 px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      사용하기
                    </button>
                  </div>
                </li>
                <li className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">
                        RSI 과매수/과매도 전략
                      </h4>
                      <p className="mt-1 text-sm text-gray-500">
                        RSI가 30 이하일 때 매수, 70 이상일 때 매도
                      </p>
                    </div>
                    <button className="ml-4 px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      사용하기
                    </button>
                  </div>
                </li>
                <li className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">
                        볼린저 밴드 돌파 전략
                      </h4>
                      <p className="mt-1 text-sm text-gray-500">
                        가격이 하단 밴드를 터치하면 매수, 상단 밴드를 터치하면 매도
                      </p>
                    </div>
                    <button className="ml-4 px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      사용하기
                    </button>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
