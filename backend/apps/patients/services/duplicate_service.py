"""Deteção de pacientes duplicados."""

from django.db.models import Q

from apps.patients.models import Patient


class DuplicateService:
    @staticmethod
    def find_potential_duplicates(
        first_name: str,
        last_name: str,
        birth_date,
        phone: str = "",
        document_number: str = "",
        exclude_id: int | None = None,
    ) -> list[dict]:
        queryset = Patient.objects.filter(is_deleted=False)

        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)

        if document_number:
            doc_match = queryset.filter(document_number=document_number)
            if doc_match.exists():
                return [DuplicateService._to_match(p, 1.0) for p in doc_match[:5]]

        matches = queryset.filter(
            Q(first_name__iexact=first_name.strip())
            | Q(last_name__iexact=last_name.strip())
            | Q(phone=phone)
        )
        if birth_date:
            matches = queryset.filter(birth_date=birth_date).filter(
                Q(first_name__iexact=first_name.strip())
                | Q(last_name__iexact=last_name.strip())
                | Q(phone=phone)
            )
        matches = matches[:10]

        results = []
        for patient in matches:
            score = DuplicateService._similarity_score(
                patient, first_name, last_name, birth_date, phone
            )
            if score >= 0.5:
                results.append(DuplicateService._to_match(patient, score))

        results.sort(key=lambda item: item["similarity_score"], reverse=True)
        return results[:5]

    @staticmethod
    def _similarity_score(patient, first_name, last_name, birth_date, phone) -> float:
        score = 0.0
        if patient.first_name.lower() == first_name.strip().lower():
            score += 0.35
        if patient.last_name.lower() == last_name.strip().lower():
            score += 0.35
        if patient.birth_date == birth_date:
            score += 0.2
        if phone and patient.phone == phone:
            score += 0.1
        return round(min(score, 1.0), 2)

    @staticmethod
    def _to_match(patient, score: float) -> dict:
        return {
            "id": patient.pk,
            "patient_number": patient.patient_number,
            "full_name": patient.full_name,
            "birth_date": patient.birth_date,
            "phone": patient.phone,
            "similarity_score": score,
        }

    @staticmethod
    def document_exists(document_number: str, exclude_id: int | None = None) -> Patient | None:
        if not document_number:
            return None
        queryset = Patient.objects.filter(
            document_number=document_number,
            is_deleted=False,
        )
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        return queryset.first()
