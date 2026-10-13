import csv
import io
import datetime
from typing import Optional
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

from backend.app.models.models import (
    Assessment, Asset, VulnerabilityFinding, SimulatedAttackPath, RemediationRecommendation
)

class ReportGeneratorService:
    """
    Generates compliance-ready CSV exports and professional PDF Security Assessment Reports.
    """

    @classmethod
    def generate_csv_report(cls, db: Session, assessment_id: Optional[int] = None) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Finding ID", "CVE ID", "Severity", "CVSS v3", "Contextual Risk (0-100)",
            "Asset Hostname", "Asset IP", "Asset Criticality", "Environment",
            "Reachability", "Match Type", "Title", "Remediation Advice", "Created At"
        ])

        query = db.query(VulnerabilityFinding)
        if assessment_id:
            query = query.filter(VulnerabilityFinding.assessment_id == assessment_id)
        findings = query.all()

        for f in findings:
            writer.writerow([
                f.id,
                f.cve_id,
                f.cvss_v3_severity,
                f.cvss_v3_score,
                f.contextual_risk_score,
                f.asset.hostname or "N/A",
                f.asset.ip_address,
                f.asset.criticality,
                f.asset.environment,
                f.reachability_status,
                f.match_type,
                f.title,
                f.remediation_advice or "N/A",
                f.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])

        return output.getvalue()

    @classmethod
    def generate_pdf_report(cls, db: Session, assessment_id: Optional[int] = None) -> bytes:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        navy = colors.HexColor("#0f172a")
        slate = colors.HexColor("#334155")
        cyan = colors.HexColor("#0284c7")
        red = colors.HexColor("#b91c1c")
        light_bg = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=navy,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=slate,
            spaceAfter=15
        )

        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=navy,
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=slate,
            spaceAfter=6
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("CYBERSECURITY DIGITAL TWIN", title_style))
        story.append(Paragraph("Vulnerability Assessment & Topology-Aware Attack Path Report", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=cyan, spaceAfter=12))

        # 2. Executive Summary
        assessment = None
        if assessment_id:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            assessment = db.query(Assessment).order_by(Assessment.id.desc()).first()

        assets = db.query(Asset).all()
        findings = db.query(VulnerabilityFinding).all()
        paths = db.query(SimulatedAttackPath).all()
        remediations = db.query(RemediationRecommendation).all()

        crit_count = sum(1 for f in findings if f.cvss_v3_severity == "CRITICAL")
        high_count = sum(1 for f in findings if f.cvss_v3_severity == "HIGH")

        story.append(Paragraph("1. Executive Summary", h2_style))
        exec_summary_text = (
            f"This security assessment was produced by the <b>AI-Powered Cybersecurity Digital Twin</b> platform. "
            f"A complete virtual model of the enterprise network was evaluated across {len(assets)} assets and {len(findings)} discovered vulnerability findings. "
            f"Unlike traditional point-in-time scanners that rank findings strictly by raw CVSS scores, this platform evaluated "
            f"<b>topological reachability</b> and simulated multi-hop lateral movement vectors to calculate context-aware risk scores. "
            f"Simulations revealed {len(paths)} potential lateral breach trajectories targeting critical internal systems."
        )
        story.append(Paragraph(exec_summary_text, body_style))

        # Metrics KPI Table
        summary_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Assets", str(len(assets)), "Total Vulnerabilities", str(len(findings))],
            ["Critical Findings", str(crit_count), "High Findings", str(high_count)],
            ["Simulated Attack Paths", str(len(paths)), "Assessment Mode", assessment.assessment_type if assessment else "Simulated Lab"]
        ]
        t_summary = Table(summary_data, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 1.2*inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_bg, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 10))

        # 3. Asset Inventory Summary
        story.append(Paragraph("2. Asset Inventory & Network Scope", h2_style))
        asset_table_data = [["IP Address", "Hostname", "Type", "Criticality", "Subnet", "Perimeter"]]
        for a in assets[:6]:
            asset_table_data.append([
                a.ip_address,
                (a.hostname or "")[:24],
                a.asset_type,
                a.criticality,
                a.subnet or "N/A",
                "YES" if a.is_perimeter else "NO"
            ])
        t_assets = Table(asset_table_data, colWidths=[1.3*inch, 2.0*inch, 0.9*inch, 0.9*inch, 1.1*inch, 0.8*inch])
        t_assets.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), slate),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_bg, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_assets)
        story.append(Spacer(1, 10))

        # 4. Key Vulnerability Findings
        story.append(Paragraph("3. Context-Aware Vulnerability Exposure", h2_style))
        vuln_table_data = [["CVE ID", "Host", "CVSS v3", "Context Risk", "Exposure", "Match Type"]]
        for f in findings[:6]:
            vuln_table_data.append([
                f.cve_id,
                (f.asset.hostname or f.asset.ip_address)[:18],
                str(f.cvss_v3_score),
                f"{f.contextual_risk_score}/100",
                f.reachability_status.replace("_", " ").title(),
                f.match_type
            ])
        t_vulns = Table(vuln_table_data, colWidths=[1.4*inch, 1.7*inch, 0.9*inch, 1.1*inch, 1.4*inch, 1.1*inch])
        t_vulns.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), slate),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_bg, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_vulns)
        story.append(Spacer(1, 10))

        # 5. Prioritized Remediation Worklist
        story.append(Paragraph("4. Algorithmic Remediation Roadmap", h2_style))
        rem_table_data = [["Priority", "Action", "Risk Delta", "Affected Paths", "Status"]]
        for r in remediations[:5]:
            rem_table_data.append([
                r.priority,
                r.title[:38],
                f"{r.risk_before:.0f} -> {r.risk_after:.0f}",
                str(r.affected_attack_paths_count),
                r.status
            ])
        t_rem = Table(rem_table_data, colWidths=[1.0*inch, 3.2*inch, 1.1*inch, 1.1*inch, 1.0*inch])
        t_rem.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_bg, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_rem)
        story.append(Spacer(1, 10))

        # 6. Methodology & Limitations
        story.append(Paragraph("5. Methodology, Boundaries & Limitations", h2_style))
        methodology_text = (
            "<b>Risk Calculation Formula:</b> Contextual Risk = Normalized CVSS × Reachability Weight × Asset Impact Weight × Confidence Factor. "
            "<br/><b>Safe Simulation:</b> Attack paths are evaluated mathematically using Dijkstra and BFS algorithms on the stored graph model. "
            "No active exploit payloads or credential theft attacks are launched against live physical systems. "
            "<br/><b>Data Freshness:</b> Vulnerability intelligence correlates with the NIST National Vulnerability Database (NVD) API and local CVE cache. "
            "Zero-day exploits not cataloged in known repositories are outside the scope of heuristic matching."
        )
        story.append(Paragraph(methodology_text, body_style))

        # Footer timestamp
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=6))
        footer_text = f"Report generated on: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Security Operations Center (SOC) | Confidential Security Assessment"
        story.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=body_style, fontSize=7, textColor=colors.gray)))

        doc.build(story)
        return pdf_buffer.getvalue()
