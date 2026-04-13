import hashlib
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Engagement, Report, Scan


class ReportService:
    def __init__(self) -> None:
        self.settings = get_settings()
        template_dir = Path(__file__).resolve().parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape())

    def generate(self, db: Session, scan: Scan, engagement: Engagement) -> Report:
        reports_dir = Path(self.settings.reports_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = reports_dir / f"{scan.id}.md"
        pdf_path = reports_dir / f"{scan.id}.pdf"

        template = self.env.get_template("report.md.j2")
        markdown = template.render(
            generated_at=datetime.now(UTC).isoformat(),
            scan=scan,
            engagement=engagement,
            summary=scan.summary,
            findings=scan.findings,
            severity_counts=scan.severity_counts,
        )
        markdown_path.write_text(markdown, encoding="utf-8")
        self._write_pdf(pdf_path, markdown)
        checksum = hashlib.sha256(markdown.encode("utf-8")).hexdigest()

        report = scan.report or Report(scan_id=scan.id, markdown_path=str(markdown_path), pdf_path=str(pdf_path), checksum=checksum)
        report.markdown_path = str(markdown_path)
        report.pdf_path = str(pdf_path)
        report.checksum = checksum
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def _write_pdf(self, pdf_path: Path, markdown: str) -> None:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        story = []
        for line in markdown.splitlines():
            if not line.strip():
                story.append(Spacer(1, 6))
                continue
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, styles["BodyText"]))
        doc.build(story)

