from __future__ import annotations

from dataclasses import dataclass, field

from src.database.csv_reader import load_medicines
from src.matching.medicine_matcher import find_best_medicine_match
from src.services.candidate_processor import (
    MatchRecord,
    count_alphabetic_characters,
    create_medicine_name_candidates,
    filter_candidate_texts,
    is_valid_base_name_candidate,
    normalize_filter_text,
    rank_medicine_matches,
)
from src.services.config import PipelineConfig

MATCHED_MESSAGE = "İlaç eşleştirildi."
NOT_FOUND_MESSAGE = "İlaç CSV veritabanında bulunamadı."
NOT_MEDICINE_BOX_MESSAGE = (
    "Tespit edilen kutu ilaç kutusu olarak doğrulanamadı."
)


def _select_display_ocr_text(
    filtered_candidates: list[str],
    ranked_matches: list[MatchRecord],
) -> str | None:
    """Eşleşme olmasa bile kullanıcıya anlamlı OCR metnini gösterir."""
    for _, _, candidate_text in ranked_matches:
        if (
            is_valid_base_name_candidate(candidate_text)
            and count_alphabetic_characters(candidate_text) >= 5
        ):
            return candidate_text

    name_like_candidates = [
        text
        for text in filtered_candidates
        if is_valid_base_name_candidate(text)
    ]

    if name_like_candidates:
        return max(
            name_like_candidates,
            key=lambda text: len(normalize_filter_text(text)),
        )

    compact_candidates = [
        text
        for text in filtered_candidates
        if len(normalize_filter_text(text).split()) <= 3
    ]

    if compact_candidates:
        return max(
            compact_candidates,
            key=lambda text: (
                count_alphabetic_characters(text),
                -len(text),
            ),
        )

    if filtered_candidates:
        return max(
            filtered_candidates,
            key=lambda text: (
                count_alphabetic_characters(text),
                len(text),
            ),
        )

    if ranked_matches:
        return ranked_matches[0][2]

    return None


def should_reject_as_non_medicine_box(
    *,
    display_match_score: float,
    display_ocr_text: str | None,
    minimum_plausible_match_score: float,
) -> bool:
    """
    YOLO false positive'lerini (UNO kutusu vb.) ilaç sonucu olarak
    göstermemek için düşük güvenilir OCR + düşük eşleşme skorunu reddeder.
    """
    if display_match_score < minimum_plausible_match_score:
        return True

    if not display_ocr_text:
        return True

    normalized_text = normalize_filter_text(display_ocr_text)

    if not normalized_text:
        return True

    if not is_valid_base_name_candidate(normalized_text):
        return True

    return False


def is_reliable_medicine_match(
    query_text: str,
    medicine_name: str,
    *,
    minimum_text_length: int,
    minimum_name_coverage_ratio: float,
) -> bool:
    """
    Kısa veya parçalı OCR metinlerinin yanlış eşleşmesini engeller.

    Tek harfli OCR çıktıları (ör. "s", "u") RapidFuzz'ta yüksek skor
    alabilir; bu kontrol güvenilir eşleşmeyi doğrular.
    """
    normalized_query = normalize_filter_text(query_text)
    normalized_name = normalize_filter_text(medicine_name)

    query_alpha_length = count_alphabetic_characters(
        normalized_query
    )
    name_alpha_length = count_alphabetic_characters(
        normalized_name
    )

    if query_alpha_length < minimum_text_length:
        return False

    if name_alpha_length == 0:
        return False

    coverage_ratio = query_alpha_length / name_alpha_length
    return coverage_ratio >= minimum_name_coverage_ratio


@dataclass
class TextMatchResult:
    """Tek bir OCR metni için CSV eşleştirme sonucu."""

    medicine_name: str | None
    medicine: dict[str, str] | None
    matching_score: float
    best_ocr_text: str | None
    best_candidate: str | None
    status: str
    display_message: str
    ranked_matches: list[MatchRecord] = field(default_factory=list)


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
        """OCR adaylarını genişletir ve eşleştirme için filtreler."""
        expanded = create_medicine_name_candidates(
            candidate_texts=candidate_texts,
        )
        filtered = filter_candidate_texts(
            candidate_texts=expanded,
            minimum_text_length=(
                self.config.minimum_matching_text_length
            ),
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

    def match_text(
        self,
        candidate_texts: list[str],
    ) -> TextMatchResult:
        """
        OCR aday metinlerini CSV ile eşleştirir.

        Skor minimum_match_score altındaysa status=not_found döner.
        """
        expanded, filtered = self.process_candidates(
            candidate_texts=candidate_texts,
        )

        if not filtered:
            return TextMatchResult(
                medicine_name=None,
                medicine=None,
                matching_score=0.0,
                best_ocr_text=None,
                best_candidate=None,
                status="not_medicine_box",
                display_message=NOT_MEDICINE_BOX_MESSAGE,
            )

        ranked_matches = self.rank_matches(
            filtered_candidates=filtered,
        )

        display_ocr_text = _select_display_ocr_text(
            filtered_candidates=filtered,
            ranked_matches=ranked_matches,
        )

        display_match_score = 0.0
        display_best_candidate: str | None = None

        if display_ocr_text:
            _, display_match_score, display_best_candidate = (
                find_best_medicine_match(
                    query_text=display_ocr_text,
                    medicines=self.medicines,
                    score_cutoff=0.0,
                )
            )

        if not ranked_matches:
            if should_reject_as_non_medicine_box(
                display_match_score=display_match_score,
                display_ocr_text=display_ocr_text,
                minimum_plausible_match_score=(
                    self.config.minimum_plausible_match_score
                ),
            ):
                return TextMatchResult(
                    medicine_name=None,
                    medicine=None,
                    matching_score=display_match_score,
                    best_ocr_text=display_ocr_text,
                    best_candidate=None,
                    status="not_medicine_box",
                    display_message=NOT_MEDICINE_BOX_MESSAGE,
                )

            return TextMatchResult(
                medicine_name=None,
                medicine=None,
                matching_score=0.0,
                best_ocr_text=display_ocr_text,
                best_candidate=None,
                status="not_found",
                display_message=NOT_FOUND_MESSAGE,
            )

        for medicine, score, ocr_text in ranked_matches:
            candidate_name = medicine.get("medicine_name")

            if score < self.config.minimum_match_score:
                continue

            if (
                ocr_text is None
                or candidate_name is None
                or not is_reliable_medicine_match(
                    query_text=ocr_text,
                    medicine_name=candidate_name,
                    minimum_text_length=(
                        self.config.minimum_matching_text_length
                    ),
                    minimum_name_coverage_ratio=(
                        self.config.minimum_name_coverage_ratio
                    ),
                )
            ):
                continue

            return TextMatchResult(
                medicine_name=candidate_name,
                medicine=medicine,
                matching_score=score,
                best_ocr_text=ocr_text,
                best_candidate=candidate_name,
                status="matched",
                display_message=MATCHED_MESSAGE,
                ranked_matches=ranked_matches,
            )

        if should_reject_as_non_medicine_box(
            display_match_score=display_match_score,
            display_ocr_text=display_ocr_text,
            minimum_plausible_match_score=(
                self.config.minimum_plausible_match_score
            ),
        ):
            return TextMatchResult(
                medicine_name=None,
                medicine=None,
                matching_score=display_match_score,
                best_ocr_text=display_ocr_text,
                best_candidate=None,
                status="not_medicine_box",
                display_message=NOT_MEDICINE_BOX_MESSAGE,
                ranked_matches=ranked_matches,
            )

        return TextMatchResult(
            medicine_name=None,
            medicine=None,
            matching_score=display_match_score,
            best_ocr_text=display_ocr_text,
            best_candidate=display_best_candidate,
            status="not_found",
            display_message=NOT_FOUND_MESSAGE,
            ranked_matches=ranked_matches,
        )
