"""Variant resources."""

from .base import BaseResource


class Variant(BaseResource):
    """ResolweBio Variant resource."""

    endpoint = "variant"

    READ_ONLY_FIELDS = BaseResource.READ_ONLY_FIELDS + (
        "species",
        "genome_assembly",
        "chromosome",
        "position",
        "reference",
        "alternative",
    )

    def __init__(self, resolwe, **model_data):
        """Initialize object."""
        super().__init__(resolwe, **model_data)
        self._annotations = None

    @property
    def annotations(self):
        """Get the annotations for this variant."""
        if self._annotations is None:
            self._annotations = self.resolwe.variant_annotation.filter(id=self.id)
        return self._annotations

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Variant <chr: {self.chromosome}, pos: {self.position}, "
            f"ref: {self.reference}, alt: {self.alternative}>"
        )


class VariantAnnotation(BaseResource):
    """VariantAnnotation resource."""

    endpoint = "variant_annotations"

    READ_ONLY_FIELDS = BaseResource.READ_ONLY_FIELDS + (
        "variant_id",
        "type",
        "clinical_diagnosis",
        "clinical_significance",
        "dbsnp_id",
        "clinvar_id",
        "data",
        "transcripts",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"VariantAnnotation <variant: {self.variant_id}>"


class VariantExperiment(BaseResource):
    """Variant experiment resource."""

    endpoint = "variant_experiment"

    READ_ONLY_FIELDS = BaseResource.READ_ONLY_FIELDS + (
        "variant_data_source",
        "timestamp",
        "contributor",
    )


class VariantCall(BaseResource):
    """VariantCall resource."""

    endpoint = "variant_calls"

    READ_ONLY_FIELDS = BaseResource.READ_ONLY_FIELDS + (
        "sample",
        "variant",
        "experiment",
        "quality",
        "depth_norm_quality",
        "alternative_allele_depth",
        "depth",
        "genotype",
        "genotype_quality",
        "filter",
        "data",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"VariantCall <pk: {self.id}>"
