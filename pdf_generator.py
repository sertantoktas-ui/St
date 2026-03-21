#!/usr/bin/env python3
"""
PDF Rapor Oluşturma - ReportLab kullanarak
HTML, Markdown, Text formatlarından PDF oluştur
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
from pathlib import Path
from typing import Optional, List

class PDFReportGenerator:
    """PDF rapor oluşturucusu"""

    def __init__(self, output_dir: str = "./reports"):
        """
        PDF oluşturucuyu başlat

        Args:
            output_dir: Raporların kaydedileceği dizin
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)

    def generate_from_text(self, title: str, content: str,
                          author: str = "Personal Assistant",
                          filename: Optional[str] = None) -> str:
        """
        Text formatından PDF oluştur

        Args:
            title: Rapor başlığı
            content: Rapor içeriği
            author: Yazar adı
            filename: Dosya adı (otomatik oluşturulur)

        Returns:
            Dosya yolu
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        # Document oluştur
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Stiller
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E5090'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        content_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        )

        # İçerik
        elements = []

        # Başlık
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        # Meta bilgiler
        meta_text = f"<b>Oluşturulma Tarihi:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/><b>Yazar:</b> {author}"
        elements.append(Paragraph(meta_text, styles['Normal']))
        elements.append(Spacer(1, 20))

        # İçerik
        for paragraph in content.split('\n\n'):
            if paragraph.strip():
                elements.append(Paragraph(paragraph, content_style))
                elements.append(Spacer(1, 8))

        # Footer
        elements.append(Spacer(1, 20))
        footer_text = f"<i>© 2024 Personal Assistant | Sayfa Sayısı: Dinamik</i>"
        elements.append(Paragraph(footer_text, styles['Normal']))

        # PDF oluştur
        doc.build(elements)
        print(f"✅ PDF oluşturuldu: {filepath}")

        return filepath

    def generate_from_markdown(self, title: str, markdown_content: str,
                              filename: Optional[str] = None) -> str:
        """
        Markdown formatından PDF oluştur

        Args:
            title: Rapor başlığı
            markdown_content: Markdown içeriği
            filename: Dosya adı

        Returns:
            Dosya yolu
        """
        # Markdown'ı basit text'e dönüştür
        text_content = self._markdown_to_text(markdown_content)
        return self.generate_from_text(title, text_content, filename=filename)

    def generate_invoice_style(self, title: str, data: dict,
                              filename: Optional[str] = None) -> str:
        """
        Fatura/Tablo stili rapor oluştur

        Args:
            title: Rapor başlığı
            data: {
                'header': 'Başlık',
                'items': [{'name': '...', 'value': '...'}, ...],
                'total': '...',
                'notes': '...'
            }
            filename: Dosya adı

        Returns:
            Dosya yolu
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoice_{timestamp}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        styles = getSampleStyleSheet()
        elements = []

        # Başlık
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1F4788'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))

        # Tarih
        date_text = f"<b>Tarih:</b> {datetime.now().strftime('%d.%m.%Y')}"
        elements.append(Paragraph(date_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Tablo
        if 'items' in data:
            table_data = [['Açıklama', 'Tutar']]
            for item in data['items']:
                table_data.append([item['name'], item['value']])

            table = Table(table_data, colWidths=[4*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Toplam
        if 'total' in data:
            total_style = ParagraphStyle(
                'Total',
                parent=styles['Normal'],
                fontSize=14,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#2E5090')
            )
            elements.append(Paragraph(f"<b>Toplam: {data['total']}</b>", total_style))
            elements.append(Spacer(1, 12))

        # Notlar
        if 'notes' in data:
            elements.append(Paragraph("<b>Notlar:</b>", styles['Normal']))
            elements.append(Paragraph(data['notes'], styles['Normal']))

        # PDF oluştur
        doc.build(elements)
        print(f"✅ Rapor PDF'si oluşturuldu: {filepath}")

        return filepath

    @staticmethod
    def _markdown_to_text(markdown: str) -> str:
        """Basit Markdown dönüştürme"""
        text = markdown
        # Başlıkları temizle
        text = text.replace('# ', '').replace('## ', '').replace('### ', '')
        # Bold'u temizle
        text = text.replace('**', '').replace('__', '')
        # İtalik'i temizle
        text = text.replace('*', '').replace('_', '')
        # Link'leri basitleştir
        text = text.replace('[', '').replace(']', '')
        text = text.replace('(', '').replace(')', '')
        return text

    def list_reports(self) -> List[str]:
        """Oluşturulan raporları listele"""
        reports = []
        if os.path.exists(self.output_dir):
            reports = [f for f in os.listdir(self.output_dir) if f.endswith('.pdf')]
        return reports

    def get_report_path(self, filename: str) -> str:
        """Rapor dosya yolunu al"""
        return os.path.join(self.output_dir, filename)


# Test
def test_pdf_generator():
    """PDF oluşturma testi"""
    generator = PDFReportGenerator()

    # Test 1: Basit text rapor
    content = """
    Bu bir test raporudur.

    Raporun ana içeriği burada yer almaktadır.
    PDF oluşturma işlemi başarılı bir şekilde gerçekleştirilmiştir.

    Sonuç: Sistem düzgün çalışmaktadır.
    """

    filepath = generator.generate_from_text(
        title="Test Raporu",
        content=content
    )

    print(f"\n📄 Test raporu: {filepath}")

    # Test 2: Fatura stili rapor
    invoice_data = {
        'items': [
            {'name': 'Konsültasyon Hizmeti', 'value': '1,000 TL'},
            {'name': 'Web Tasarımı', 'value': '2,500 TL'},
            {'name': 'Yazılım Geliştirme', 'value': '5,000 TL'}
        ],
        'total': '8,500 TL',
        'notes': 'Ödeme şartları: 30 gün içinde'
    }

    invoice_path = generator.generate_invoice_style(
        title="Fatura",
        data=invoice_data
    )

    print(f"📄 Fatura PDF: {invoice_path}")

    # Raporları listele
    reports = generator.list_reports()
    print(f"\n📋 Oluşturulan Raporlar ({len(reports)} adet):")
    for report in reports:
        print(f"   - {report}")


if __name__ == "__main__":
    test_pdf_generator()
