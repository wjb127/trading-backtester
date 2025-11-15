"""
백테스트 리포트 생성 서비스
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
import io
from typing import Dict, List, Any


class ReportGenerator:
    """백테스트 리포트 생성기"""

    def __init__(self, filename: str):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []

        # 커스텀 스타일 추가
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=12
        ))

    def add_title(self, title: str):
        """제목 추가"""
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.2 * inch))

    def add_section(self, heading: str):
        """섹션 제목 추가"""
        self.story.append(Spacer(1, 0.3 * inch))
        self.story.append(Paragraph(heading, self.styles['CustomHeading']))
        self.story.append(Spacer(1, 0.1 * inch))

    def add_paragraph(self, text: str):
        """본문 추가"""
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.1 * inch))

    def add_table(self, data: List[List[str]], col_widths: List[float] = None):
        """테이블 추가"""
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * inch))

    def add_chart(self, equity_curve: List[Dict[str, Any]], title: str = "Portfolio Equity Curve"):
        """차트 추가"""
        # 데이터 준비
        timestamps = [point['timestamp'] for point in equity_curve]
        values = [point['value'] for point in equity_curve]

        # 그래프 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(values, linewidth=2, color='#3B82F6')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.grid(True, alpha=0.3)

        # 이미지를 메모리에 저장
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        # 리포트에 추가
        img = Image(img_buffer, width=6*inch, height=3.6*inch)
        self.story.append(img)
        self.story.append(Spacer(1, 0.2 * inch))

    def generate_backtest_report(
        self,
        backtest_data: Dict[str, Any],
        trades: List[Dict[str, Any]],
        equity_curve: List[Dict[str, Any]]
    ):
        """백테스트 전체 리포트 생성"""

        # 제목
        self.add_title("Trading Backtest Report")

        # 생성 정보
        self.add_paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.add_paragraph(f"<b>Symbol:</b> {backtest_data.get('symbol', 'N/A')}")
        self.add_paragraph(f"<b>Period:</b> {backtest_data.get('start_date', 'N/A')} ~ {backtest_data.get('end_date', 'N/A')}")

        # 성과 요약
        self.add_section("Performance Summary")

        metrics_data = [
            ['Metric', 'Value'],
            ['Initial Capital', f"${backtest_data.get('initial_capital', 0):,.2f}"],
            ['Final Capital', f"${backtest_data.get('final_capital', 0):,.2f}"],
            ['Total Return', f"{backtest_data.get('total_return', 0):.2f}%"],
            ['Max Drawdown', f"{backtest_data.get('max_drawdown', 0):.2f}%"],
            ['Sharpe Ratio', f"{backtest_data.get('sharpe_ratio', 0):.2f}"],
            ['Total Trades', str(backtest_data.get('total_trades', 0))],
            ['Win Rate', f"{backtest_data.get('win_rate', 0):.2f}%"],
        ]

        self.add_table(metrics_data, col_widths=[3*inch, 3*inch])

        # 수익 곡선 차트
        if equity_curve:
            self.add_section("Equity Curve")
            self.add_chart(equity_curve)

        # 거래 기록
        if trades:
            self.add_section("Trade History")

            trades_data = [['Date', 'Action', 'Price', 'Quantity', 'Balance']]
            for trade in trades[:20]:  # 최근 20개 거래만 표시
                trades_data.append([
                    trade.get('timestamp', ''),
                    trade.get('action', '').upper(),
                    f"${trade.get('price', 0):.2f}",
                    f"{trade.get('quantity', 0):.4f}",
                    f"${trade.get('balance', 0):,.2f}"
                ])

            self.add_table(trades_data, col_widths=[1.5*inch, 1*inch, 1.2*inch, 1.2*inch, 1.5*inch])

            if len(trades) > 20:
                self.add_paragraph(f"<i>Showing 20 of {len(trades)} total trades</i>")

        # 면책 조항
        self.add_section("Disclaimer")
        self.add_paragraph(
            "<i>This backtest report is for informational purposes only. "
            "Past performance does not guarantee future results. "
            "Trading involves risk and may not be suitable for all investors.</i>"
        )

    def save(self):
        """PDF 저장"""
        self.doc.build(self.story)
        return self.filename
