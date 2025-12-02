# app/shared/toon_parser.py
import logging
import re

import yaml

logger = logging.getLogger(__name__)


def _normalize_counts(obj):
    """
    Normalisasi key TOON dengan format `key[count]` menjadi `key`.
    Berlaku rekursif untuk struktur dict/list.
    Contoh:
      - questions[3] -> questions
      - positive[2] -> positive
    """

    # Fungsi bantu untuk menghapus suffix [number] pada key
    def _strip_count(key: str) -> str:
        # Hapus pattern [angka] di akhir key
        return re.sub(r"\[\d+\]$", "", key)

    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            new_key = _strip_count(k)
            new_dict[new_key] = _normalize_counts(v)
        return new_dict
    elif isinstance(obj, list):
        return [_normalize_counts(v) for v in obj]
    else:
        return obj


def parse_toon_string(raw_text: str) -> dict:
    """
    Mengubah string output LLM (format TOON/YAML) menjadi Python Dictionary.
    Menggunakan PyYAML karena TOON valid adalah YAML valid.
    """
    try:
        # 1. Bersihkan Markdown wrapper (jika AI menambahkan ```yaml)
        clean_text = (
            raw_text.replace("```yaml", "")
            .replace("```json", "")  # Jaga-jaga jika AI salah label
            .replace("```", "")
            .strip()
        )

        # 2. Parse menggunakan PyYAML
        # safe_load adalah standar keamanan untuk mencegah eksekusi kode berbahaya
        data = yaml.safe_load(clean_text)

        # 3. Validasi tipe data (harus Dict atau List)
        if not isinstance(data, (dict, list)):
            raise ValueError("Hasil parsing bukan Dictionary atau List valid.")

        # 4. Normalisasi key TOON agar sesuai schema Pydantic:
        #    - questions[1] -> questions
        #    - positive[2]  -> positive
        normalized = _normalize_counts(data)

        return normalized

    except yaml.YAMLError as e:
        logger.error(f"YAML Parsing Error: {e}")
        logger.debug(f"Raw text was: {raw_text}")
        raise ValueError("AI Output is not in valid TOON/YAML format")

    except Exception as e:
        logger.error(f"General Parsing Error: {e}")
        raise e
