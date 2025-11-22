"""
PDF Report Generator - Create comprehensive performance analysis reports
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from utils.protocol_logger import logger


class PDFReportGenerator:
    """Generate multi-page PDF reports with graphs, statistics, and alerts"""

    def __init__(self):
        """Initialize PDF generator"""
        if not REPORTLAB_AVAILABLE:
            logger.warning("HEALTH", "reportlab not available - PDF export disabled")
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            # Add custom styles
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#003366'),
                spaceAfter=30,
                alignment=1  # Center
            ))
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#004080'),
                spaceAfter=12,
                spaceBefore=12
            ))

        logger.debug("HEALTH", f"PDFReportGenerator initialized (reportlab available: {REPORTLAB_AVAILABLE})")

    def generate_report(
        self,
        output_path: str,
        readiness_data: Dict[str, Any],
        statistics: Dict[str, Any],
        alerts: List[Any],
        graphs_figure: Optional[Any] = None,
        correlation_figure: Optional[Any] = None
    ) -> bool:
        """
        Generate comprehensive PDF report

        Args:
            output_path: Path to save PDF file
            readiness_data: Mission readiness data
            statistics: Performance statistics
            alerts: List of anomaly alerts
            graphs_figure: Matplotlib figure with performance graphs
            correlation_figure: Matplotlib figure with correlation heatmap

        Returns:
            True if successful, False otherwise
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("HEALTH", "Cannot generate PDF - reportlab not installed")
            return False

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            # Build content
            story = []

            # Title Page
            story.append(Paragraph("DPM Performance Analysis Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 0.5*inch))

            # Mission Readiness Section
            if readiness_data:
                story.extend(self._create_readiness_section(readiness_data))
                story.append(PageBreak())

            # Performance Graphs
            if graphs_figure:
                story.append(Paragraph("Performance Metrics", self.styles['SectionHeader']))
                story.append(Spacer(1, 0.2*inch))

                # Convert matplotlib figure to image
                img_buffer = io.BytesIO()
                graphs_figure.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                img_buffer.seek(0)

                # Add image to PDF
                img = Image(img_buffer, width=7*inch, height=8.5*inch)
                story.append(img)
                story.append(PageBreak())

            # Statistics Section
            if statistics:
                story.extend(self._create_statistics_section(statistics))
                story.append(PageBreak())

            # Correlation Analysis
            if correlation_figure:
                story.append(Paragraph("Correlation Analysis", self.styles['SectionHeader']))
                story.append(Spacer(1, 0.2*inch))

                # Convert correlation figure to image
                img_buffer = io.BytesIO()
                correlation_figure.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                img_buffer.seek(0)

                img = Image(img_buffer, width=6.5*inch, height=6*inch)
                story.append(img)
                story.append(PageBreak())

            # Alerts Section
            if alerts:
                story.extend(self._create_alerts_section(alerts))

            # Build PDF
            doc.build(story)

            logger.info("HEALTH", f"PDF report generated: {output_path}")
            return True

        except Exception as e:
            logger.error("HEALTH", f"Failed to generate PDF report: {e}")
            return False

    def _create_readiness_section(self, readiness_data: Dict[str, Any]) -> List:
        """Create mission readiness section"""
        elements = []

        elements.append(Paragraph("Mission Readiness Assessment", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        # Overall score
        overall_score = readiness_data.get('overall_score', 0)
        overall_status = readiness_data.get('overall_status', 'UNKNOWN')

        # Determine color based on score
        if overall_score >= 90:
            score_color = colors.green
        elif overall_score >= 75:
            score_color = colors.orange
        elif overall_score >= 50:
            score_color = colors.orangered
        else:
            score_color = colors.red

        # Overall score table
        score_data = [
            ['Overall Readiness Score', f'{overall_score}%'],
            ['Status', overall_status]
        ]

        score_table = Table(score_data, colWidths=[3*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (1, 0), (1, 0), score_color),  # Color the score
        ]))

        elements.append(score_table)
        elements.append(Spacer(1, 0.3*inch))

        # Component breakdown
        elements.append(Paragraph("Component Breakdown", self.styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))

        component_data = [['Component', 'Score', 'Status']]
        components = readiness_data.get('component_scores', {})

        for component, data in components.items():
            component_data.append([
                component.capitalize(),
                f"{data['score']}%",
                data['status']
            ])

        component_table = Table(component_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(component_table)
        elements.append(Spacer(1, 0.3*inch))

        # Recommendations
        recommendations = readiness_data.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("Recommendations", self.styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))

            for rec in recommendations:
                elements.append(Paragraph(f"• {rec}", self.styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))

        return elements

    def _create_statistics_section(self, statistics: Dict[str, Any]) -> List:
        """Create statistics summary section"""
        elements = []

        elements.append(Paragraph("Performance Statistics", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        # Create summary table
        stats_data = [['Metric', 'Mean', 'Min', 'Max', 'Std Dev', 'P95']]

        # Add each metric
        for metric_key, stats in statistics.items():
            if stats.get('valid_points', 0) > 0:
                desc = stats.get('descriptive', {})
                perc = stats.get('percentiles', {})

                metric_name = stats.get('metric', metric_key).replace('_', ' ').title()

                stats_data.append([
                    metric_name,
                    f"{desc.get('mean', 0):.1f}",
                    f"{desc.get('min', 0):.1f}",
                    f"{desc.get('max', 0):.1f}",
                    f"{desc.get('std_dev', 0):.1f}",
                    f"{perc.get('p95', 0):.1f}"
                ])

        stats_table = Table(stats_data, colWidths=[1.8*inch, 1*inch, 0.9*inch, 0.9*inch, 1*inch, 0.9*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(stats_table)

        return elements

    def _create_alerts_section(self, alerts: List[Any]) -> List:
        """Create alerts section"""
        elements = []

        elements.append(Paragraph("Anomaly Detection Alerts", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        if not alerts:
            elements.append(Paragraph("No alerts detected", self.styles['Normal']))
            return elements

        # Create alerts table
        alert_data = [['Severity', 'Time', 'Message']]

        for alert in alerts[-20:]:  # Last 20 alerts
            severity = alert.severity.value.upper() if hasattr(alert, 'severity') else 'UNKNOWN'
            timestamp = alert.timestamp.strftime('%H:%M:%S') if hasattr(alert, 'timestamp') else 'N/A'
            message = alert.message if hasattr(alert, 'message') else 'No message'

            # Truncate long messages
            if len(message) > 60:
                message = message[:57] + "..."

            alert_data.append([severity, timestamp, message])

        alert_table = Table(alert_data, colWidths=[1.2*inch, 1.2*inch, 4.5*inch])
        alert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(alert_table)

        return elements
