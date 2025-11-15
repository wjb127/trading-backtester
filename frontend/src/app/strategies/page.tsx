'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Strategy {
  id: string
  name: string
  description: string
  code: string
  parameters: any
  is_active: boolean
  created_at: string
}

const exampleStrategies = [
  {
    name: '이동평균 크로스오버 (MA Crossover)',
    description: '단기 이동평균이 장기 이동평균을 상향 돌파할 때 매수, 하향 돌파할 때 매도',
    code: `def strategy(data):
    short_ma = data['close'].rolling(window=20).mean()
    long_ma = data['close'].rolling(window=50).mean()

    signals = []
    for i in range(len(data)):
        if short_ma[i] > long_ma[i] and short_ma[i-1] <= long_ma[i-1]:
            signals.append('buy')
        elif short_ma[i] < long_ma[i] and short_ma[i-1] >= long_ma[i-1]:
            signals.append('sell')
        else:
            signals.append('hold')

    return signals`,
    parameters: { short_period: 20, long_period: 50 }
  },
  {
    name: 'RSI 과매수/과매도 전략',
    description: 'RSI가 30 이하일 때 매수, 70 이상일 때 매도',
    code: `def strategy(data):
    rsi_period = 14
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    signals = []
    for i in range(len(data)):
        if rsi[i] < 30:
            signals.append('buy')
        elif rsi[i] > 70:
            signals.append('sell')
        else:
            signals.append('hold')

    return signals`,
    parameters: { rsi_period: 14, oversold: 30, overbought: 70 }
  },
  {
    name: '볼린저 밴드 돌파 전략',
    description: '가격이 하단 밴드를 터치하면 매수, 상단 밴드를 터치하면 매도',
    code: `def strategy(data):
    period = 20
    std_dev = 2

    sma = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()

    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)

    signals = []
    for i in range(len(data)):
        if data['close'][i] <= lower_band[i]:
            signals.append('buy')
        elif data['close'][i] >= upper_band[i]:
            signals.append('sell')
        else:
            signals.append('hold')

    return signals`,
    parameters: { period: 20, std_dev: 2 }
  }
]

export default function Strategies() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    code: '',
    parameters: '{}'
  })

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/strategies')
      const data = await response.json()
      setStrategies(data.strategies || [])
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStrategy = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description,
          code: formData.code,
          parameters: JSON.parse(formData.parameters || '{}')
        }),
      })

      if (response.ok) {
        setShowModal(false)
        setFormData({ name: '', description: '', code: '', parameters: '{}' })
        fetchStrategies()
      }
    } catch (error) {
      console.error('Failed to create strategy:', error)
    }
  }

  const handleUseExample = async (example: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: example.name,
          description: example.description,
          code: example.code,
          parameters: example.parameters
        }),
      })

      if (response.ok) {
        fetchStrategies()
        alert('전략이 추가되었습니다!')
      }
    } catch (error) {
      console.error('Failed to use example:', error)
    }
  }

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
            <button
              onClick={() => setShowModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
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
              {loading ? (
                <div className="text-center py-12">로딩 중...</div>
              ) : strategies.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📊</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    아직 생성된 전략이 없습니다
                  </h3>
                  <p className="text-gray-500 mb-6">
                    첫 번째 트레이딩 전략을 만들어보세요
                  </p>
                  <button
                    onClick={() => setShowModal(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    전략 만들기
                  </button>
                </div>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {strategies.map((strategy) => (
                    <li key={strategy.id} className="py-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900">
                            {strategy.name}
                          </h4>
                          <p className="mt-1 text-sm text-gray-500">
                            {strategy.description}
                          </p>
                        </div>
                        <div className="ml-4 flex space-x-2">
                          <button className="px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                            편집
                          </button>
                          <button className="px-3 py-1 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50">
                            삭제
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
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
                {exampleStrategies.map((example, index) => (
                  <li key={index} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-gray-900">
                          {example.name}
                        </h4>
                        <p className="mt-1 text-sm text-gray-500">
                          {example.description}
                        </p>
                      </div>
                      <button
                        onClick={() => handleUseExample(example)}
                        className="ml-4 px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        사용하기
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* 전략 생성 모달 */}
      {showModal && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowModal(false)}></div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  새 전략 만들기
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">전략 이름</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">설명</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={3}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">코드</label>
                    <textarea
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                      rows={10}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-sm"
                      placeholder="def strategy(data):&#10;    # 전략 코드 작성&#10;    return signals"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">파라미터 (JSON)</label>
                    <input
                      type="text"
                      value={formData.parameters}
                      onChange={(e) => setFormData({ ...formData, parameters: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                      placeholder='{"period": 20}'
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={handleCreateStrategy}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  생성
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  취소
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
