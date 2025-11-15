'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format } from 'date-fns'

interface Strategy {
  id: string
  name: string
}

interface Backtest {
  id: string
  strategy_id: string
  symbol: string
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number
  total_return: number
  max_drawdown: number
  sharpe_ratio: number
  total_trades: number
  win_rate: number
  status: string
  created_at: string
}

interface ChartData {
  equity_curve: Array<{timestamp: string, value: number}>
  trades: Array<any>
  market_data: Array<any>
}

export default function Backtests() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [backtests, setBacktests] = useState<Backtest[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedBacktest, setSelectedBacktest] = useState<string | null>(null)
  const [chartData, setChartData] = useState<ChartData | null>(null)

  const [formData, setFormData] = useState({
    strategy_id: '',
    symbol: 'AAPL',
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    initial_capital: 10000
  })

  useEffect(() => {
    fetchStrategies()
    fetchBacktests()
  }, [])

  const fetchStrategies = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/strategies')
      const data = await response.json()
      setStrategies(data.strategies || [])
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    }
  }

  const fetchBacktests = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/backtests')
      const data = await response.json()
      setBacktests(data.backtests || [])
    } catch (error) {
      console.error('Failed to fetch backtests:', error)
    }
  }

  const handleRunBacktest = async () => {
    if (!formData.strategy_id) {
      alert('전략을 선택해주세요')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/backtests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        const result = await response.json()
        alert(`백테스트 완료!\n수익률: ${result.metrics.total_return}%\n거래 횟수: ${result.metrics.total_trades}`)
        fetchBacktests()
      } else {
        const error = await response.json()
        alert(`백테스트 실패: ${error.detail}`)
      }
    } catch (error) {
      console.error('Failed to run backtest:', error)
      alert('백테스트 실행 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleViewChart = async (backtest_id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analytics/chart?backtest_id=${backtest_id}`)
      const data = await response.json()
      setChartData(data)
      setSelectedBacktest(backtest_id)
    } catch (error) {
      console.error('Failed to fetch chart data:', error)
    }
  }

  const handleDownloadPDF = async (backtest_id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/backtests/${backtest_id}/report`)

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `backtest_report_${backtest_id}.pdf`
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Failed to download PDF:', error)
      alert('PDF 다운로드 실패')
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
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md"
              >
                전략 관리
              </Link>
              <Link
                href="/backtests"
                className="text-blue-600 font-medium px-3 py-2 rounded-md"
              >
                백테스팅
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">백테스팅</h1>

          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                백테스트 설정
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                전략과 기간을 선택하여 백테스팅을 시작하세요
              </p>
            </div>
            <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
              <div className="grid grid-cols-1 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    전략 선택
                  </label>
                  <select
                    value={formData.strategy_id}
                    onChange={(e) => setFormData({ ...formData, strategy_id: e.target.value })}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md border"
                  >
                    <option value="">전략을 선택하세요</option>
                    {strategies.map((strategy) => (
                      <option key={strategy.id} value={strategy.id}>
                        {strategy.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      심볼
                    </label>
                    <input
                      type="text"
                      value={formData.symbol}
                      onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                      placeholder="예: AAPL, BTC-USD"
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      초기 자본
                    </label>
                    <input
                      type="number"
                      value={formData.initial_capital}
                      onChange={(e) => setFormData({ ...formData, initial_capital: Number(e.target.value) })}
                      placeholder="10000"
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      시작일
                    </label>
                    <input
                      type="date"
                      value={formData.start_date}
                      onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      종료일
                    </label>
                    <input
                      type="date"
                      value={formData.end_date}
                      onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div>
                  <button
                    onClick={handleRunBacktest}
                    disabled={loading}
                    className="w-full sm:w-auto inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? '실행 중...' : '백테스팅 시작'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 차트 영역 */}
          {chartData && (
            <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  수익 곡선
                </h3>
              </div>
              <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData.equity_curve}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(value) => format(new Date(value), 'MM/dd')}
                    />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#3B82F6"
                      name="Portfolio Value"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* 백테스팅 기록 */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                백테스팅 기록
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                실행된 백테스팅 결과를 확인하세요
              </p>
            </div>

            <div className="px-4 py-5 sm:p-6">
              {backtests.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📈</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    아직 백테스팅 기록이 없습니다
                  </h3>
                  <p className="text-gray-500 mb-6">
                    위의 설정을 입력하고 백테스팅을 시작해보세요
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">심볼</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">기간</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">수익률</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">최대낙폭</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">샤프비율</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">거래횟수</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {backtests.map((backtest) => (
                        <tr key={backtest.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {backtest.symbol}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {backtest.start_date} ~ {backtest.end_date}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${backtest.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {backtest.total_return}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {backtest.max_drawdown}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {backtest.sharpe_ratio}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {backtest.total_trades}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button
                              onClick={() => handleViewChart(backtest.id)}
                              className="text-blue-600 hover:text-blue-900 mr-3"
                            >
                              차트 보기
                            </button>
                            <button
                              onClick={() => handleDownloadPDF(backtest.id)}
                              className="text-green-600 hover:text-green-900"
                            >
                              PDF
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
