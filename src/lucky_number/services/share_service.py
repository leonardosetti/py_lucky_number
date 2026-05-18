"""Export & Share service — CSV, JSON, PDF generation and WhatsApp sharing."""
import csv
import io
import json
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.combinacao import Combinacao
from lucky_number.database.models.promessa import Promessa
from lucky_number.database.models.notification import SystemNotification

SHARING_TTL_DAYS = 7


async def get_user_combinations(user_id: str) -> list[dict]:
    """Fetch all combinations for a user."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Combinacao).where(Combinacao.user_id == user_id).order_by(Combinacao.created_at.desc())
        )
        return [
            {"jogo": c.jogo, "dezenas": c.dezenas, "favorita": c.favorita, "created_at": str(c.created_at.date())}
            for c in result.scalars().all()
        ]


def generate_csv(combinations: list[dict]) -> str:
    """Generate CSV string from combinations. Prevents CWE-79: output encoding."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["jogo", "dezenas", "favorita", "data"])
    for c in combinations:
        dezenas_str = " ".join(str(d) for d in c["dezenas"])
        writer.writerow([c["jogo"], dezenas_str, str(c["favorita"]), c["created_at"]])
    return output.getvalue()


def generate_json(combinations: list[dict]) -> str:
    """Generate JSON string from combinations."""
    return json.dumps(combinations, ensure_ascii=False, indent=2)


async def generate_pdf(user_id: str) -> bytes:
    """Generate PDF from combinations. Uses ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
    except ImportError:
        raise RuntimeError("ReportLab não instalado. Execute: pip install reportlab")

    combos = await get_user_combinations(user_id)
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setFont("Helvetica", 10)
    p.drawString(20 * mm, 280 * mm, "Lucky Number — Combinações")
    p.setFont("Helvetica", 8)
    y = 270 * mm
    for c in combos:
        dezenas = " ".join(str(d) for d in c["dezenas"])
        line = f"{c['jogo']}: {dezenas} — {c['data']}"
        p.drawString(20 * mm, y, line)
        y -= 5 * mm
        if y < 20 * mm:
            p.showPage()
            y = 280 * mm
    p.save()
    return buf.getvalue()


def format_whatsapp_text(combinations: list[dict]) -> str:
    """Format combinations as plain text for WhatsApp sharing.
    Prevents CWE-79: no HTML or encoding — pure plain text.
    Format: Mega-Sena: 03-12-23-34-45-56
    """
    lines = ["🍀 Lucky Number — Minhas Combinações", ""]
    for c in combinations:
        dezenas = "-".join(f"{d:02d}" for d in c["dezenas"])
        lines.append(f"{c['jogo']}: {dezenas}")
    return "\n".join(lines)


def format_clipboard(combinations: list[dict]) -> str:
    """Format combinations as plain text for clipboard copy."""
    lines = []
    for c in combinations:
        dezenas = " ".join(str(d) for d in c["dezenas"])
        lines.append(f"{c['jogo']}\t{dezenas}\t{c['data']}")
    return "\n".join(lines)


async def share_with_user(sender_id: str, recipient_id: str, combinations: list[dict]) -> bool:
    """Share combinations with another user via notification."""
    text = format_whatsapp_text(combinations)
    async with async_session_factory() as session:
        notif = SystemNotification(
            titulo="Combinações compartilhadas com você",
            mensagem=text[:500],
            prioridade="media",
            destinatario_user_id=recipient_id,
            created_by=sender_id,
        )
        session.add(notif)
        await session.commit()
        return True
