from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def write_text_report(path: Path, title: str, sections: dict) -> None:
    lines = [title, "=" * len(title), ""]
    for heading, body in sections.items():
        lines.extend([heading, "-" * len(heading), str(body).strip(), ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_pdf_report(path: Path, title: str, sections: dict) -> None:
    with PdfPages(path) as pdf:
        for heading, body in sections.items():
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.suptitle(title, fontsize=16, weight="bold", y=0.97)
            text = f"{heading}\n\n{str(body).strip()}"
            fig.text(0.08, 0.91, text, va="top", ha="left", wrap=True, fontsize=10)
            plt.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def dataframe_snapshot(df: pd.DataFrame, rows: int = 10) -> str:
    if df.empty:
        return "No records available."
    return df.head(rows).to_string(index=False)
