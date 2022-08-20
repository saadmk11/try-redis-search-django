from typing import List, Optional

from django.db import models
from redis_om import Field

from redis_search_django.documents import EmbeddedJsonDocument, JsonDocument

from .models import Category, Product, Tag, Vendor


class CategoryDocument(EmbeddedJsonDocument):
    custom_field: str = Field(index=True, full_text_search=True)

    class Django:
        model = Category
        fields = ["name", "slug"]

    @classmethod
    def prepare_custom_field(cls, obj):
        return "CUSTOM FIELD VALUE"


class TagDocument(EmbeddedJsonDocument):

    class Django:
        model = Tag
        fields = ["name"]


class VendorDocument(EmbeddedJsonDocument):

    class Django:
        model = Vendor
        fields = ["identifier", "name", "email", "establishment_date"]


class ProductDocument(JsonDocument):
    # OnetoOneField
    vendor: VendorDocument
    # ForeignKey field
    category: Optional[CategoryDocument]
    # ManyToManyField
    tags: List[TagDocument]

    class Django:
        model = Product
        fields = ["name", "description", "price", "created_at", "quantity", "available"]
        related_models = {
            Vendor: {
                "related_name": "product",
                "many": False,
            },
            Category: {
                "related_name": "product_set",
                "many": True,
            },
            Tag: {
                "related_name": "product_set",
                "many": True,
            },
        }

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return super().get_queryset().filter(available=True)

    @classmethod
    def prepare_name(cls, obj):
        return obj.name.upper()
