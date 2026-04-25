from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHEEL_LIBS = ROOT.parent / ".wheel_libs"

if str(WHEEL_LIBS) not in sys.path:
    sys.path.insert(0, str(WHEEL_LIBS))

from pypdf import PdfReader  # type: ignore


DEFAULT_PDF_PATH = Path(
    r"C:\Users\Vini\Downloads\tabela_monte_tivoli_-_residencial_abril_2026 (1).pdf"
)
OUTPUT_PATH = ROOT / "data" / "units.json"

STATUS_RE = re.compile(r"(Dispon.vel|Reservada|Bloqueada|Vendida)R\$")
HEAD_RE = re.compile(r"^(\d{3,4})\s+([\d,]+)\s*m.?(.*)$")
PRICE_RE = re.compile(r"R\$\s*([\d\.]+,\d{2})")


COLUMN_META = {
    "01": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "tarde",
        "posicao_solar_label": "Sol da tarde",
        "planta": "assets/plants/area-53-54.jpg",
        "colunas_planta": "01, 03, 06 e 08",
    },
    "02": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "tarde",
        "posicao_solar_label": "Sol da tarde",
        "planta": "assets/plants/area-51-75.jpg",
        "colunas_planta": "02 e 07",
    },
    "03": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "tarde",
        "posicao_solar_label": "Sol da tarde",
        "planta": "assets/plants/area-53-54.jpg",
        "colunas_planta": "01, 03, 06 e 08",
    },
    "04": {
        "tipologia": "2 quartos",
        "tipologia_curta": "2Q sem suite",
        "posicao_solar": "tarde",
        "posicao_solar_label": "Sol da tarde",
        "planta": "assets/plants/area-49-90.jpg",
        "colunas_planta": "04 e 10",
    },
    "05": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "tarde",
        "posicao_solar_label": "Sol da tarde",
        "planta": "assets/plants/area-53-67.jpg",
        "colunas_planta": "05",
    },
    "06": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "manha",
        "posicao_solar_label": "Sol da manha",
        "planta": "assets/plants/area-53-54.jpg",
        "colunas_planta": "01, 03, 06 e 08",
    },
    "07": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "manha",
        "posicao_solar_label": "Sol da manha",
        "planta": "assets/plants/area-51-75.jpg",
        "colunas_planta": "02 e 07",
    },
    "08": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "manha",
        "posicao_solar_label": "Sol da manha",
        "planta": "assets/plants/area-53-54.jpg",
        "colunas_planta": "01, 03, 06 e 08",
    },
    "09": {
        "tipologia": "2 quartos com suite",
        "tipologia_curta": "2Q com suite",
        "posicao_solar": "manha",
        "posicao_solar_label": "Sol da manha",
        "planta": "assets/plants/area-51-15.jpg",
        "colunas_planta": "09",
    },
    "10": {
        "tipologia": "2 quartos",
        "tipologia_curta": "2Q sem suite",
        "posicao_solar": "manha",
        "posicao_solar_label": "Sol da manha",
        "planta": "assets/plants/area-49-90.jpg",
        "colunas_planta": "04 e 10",
    },
}

STATUS_MAP = {
    "Disponível": "disponivel",
    "Reservada": "reservada",
    "Bloqueada": "bloqueada",
    "Vendida": "vendida",
}


def money_to_float(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def normalize_status(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith("dispon"):
        return "disponivel"
    if lowered.startswith("reserv"):
        return "reservada"
    if lowered.startswith("bloq"):
        return "bloqueada"
    if lowered.startswith("vend"):
        return "vendida"
    raise ValueError(f"Status nao reconhecido: {value}")


def extract_apartment_lines(pdf_path: Path) -> list[str]:
    text = "\n".join((page.extract_text() or "") for page in PdfReader(str(pdf_path)).pages)
    return [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^\d{3,4}\s", line.strip())
    ]


def build_units(rows: list[str]) -> list[dict[str, object]]:
    units: list[dict[str, object]] = []

    for row in rows:
        status_match = STATUS_RE.search(row)
        if not status_match:
            raise ValueError(f"Linha sem status reconhecido: {row}")

        head = HEAD_RE.match(row[: status_match.start(1)])
        if not head:
            raise ValueError(f"Linha sem cabecalho reconhecido: {row}")

        prices = PRICE_RE.findall(row[status_match.end(1) :])
        if len(prices) != 9:
            raise ValueError(f"Linha com quantidade inesperada de valores: {row}")

        unidade_id = head.group(1)
        pavimento = int(unidade_id[:-2])
        coluna = unidade_id[-2:]
        meta = COLUMN_META[coluna]
        entrada = money_to_float(prices[1])

        units.append(
            {
                "id": unidade_id,
                "pavimento": pavimento,
                "coluna": coluna,
                "area_privativa": round(float(head.group(2).replace(",", ".")), 2),
                "tipologia": meta["tipologia"],
                "tipologia_curta": meta["tipologia_curta"],
                "colunas_planta": meta["colunas_planta"],
                "posicao_solar": meta["posicao_solar"],
                "posicao_solar_label": meta["posicao_solar_label"],
                "status": normalize_status(status_match.group(1)),
                "valor_total": money_to_float(prices[0]),
                "entrada": entrada,
                "entrada_promocional": max(round(entrada - 5000, 2), 0),
                "mensal": money_to_float(prices[2]),
                "anual": money_to_float(prices[4]),
                "financiamento": money_to_float(prices[6]),
                "fgts": money_to_float(prices[7]),
                "planta": meta["planta"],
            }
        )

    return sorted(units, key=lambda item: (item["pavimento"], item["coluna"]))


def main() -> None:
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF_PATH
    rows = extract_apartment_lines(pdf_path)
    units = build_units(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(units, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"{len(units)} unidades salvas em {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
