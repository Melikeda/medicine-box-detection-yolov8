from __future__ import annotations

from src.database.csv_reader import load_medicines
from src.services.candidate_processor import (
    MatchRecord,
    create_medicine_name_candidates,
    filter_candidate_texts,
    rank_medicine_matches,
)
from src.services.config import PipelineConfig


class MatchingService:
    """CSV veritabanı yükleme ve RapidFuzz eşleştirme servisi."""

    def __init__(
        self,
        config: PipelineConfig,
        medicines: list[dict[str, str]],
    ) -> None:
        self.config = config
        self.medicines = medicines

    @classmethod
    def from_csv(
        cls,
        config: PipelineConfig,
    ) -> MatchingService:
        """CSV dosyasından ilaç veritabanını yükler."""
        medicines = load_medicines(
            csv_path=config.medicines_csv_path,
        )
        return cls(config=config, medicines=medicines)

    @property
    def medicine_count(self) -> int:
        return len(self.medicines)

    def process_candidates(
        self,
        candidate_texts: list[str],
    ) -> tuple[list[str], list[str]]:
        """
        OCR adaylarını genişletir ve eşleştirme için filtreler.

        Returns:
            (genişletilmiş adaylar, filtrelenmiş adaylar)
        """
        expanded = create_medicine_name_candidates(
            candidate_texts=candidate_texts,
        )
        filtered = filter_candidate_texts(
            candidate_texts=expanded,
        )
        return expanded, filtered

    def rank_matches(
        self,
        filtered_candidates: list[str],
    ) -> list[MatchRecord]:
        """Filtrelenmiş adayları veritabanıyla karşılaştırır."""
        return rank_medicine_matches(
            candidate_texts=filtered_candidates,
            medicines=self.medicines,
            top_count=self.config.top_match_count,
        )
