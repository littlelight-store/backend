from core.application.repositories.order import AbstractReviewRepository
from core.domain.entities.review import Review
from orders.repository import DjangoOrderRepository

from .models import Review as ReviewORM


class DjangoReviewRepository(AbstractReviewRepository):
    def create_review(self, review: Review):
        review_orm = ReviewORM.objects.create(
            author_id=review.author.client_id,
            order_id=review.parent_order_id,
        )
        review_orm.services.set([order.service.slug for order in review.orders])
        return self._encode_review(review_orm)

    @staticmethod
    def _encode_review(
        review: ReviewORM
    ) -> Review:
        return Review(
            author=DjangoOrderRepository.encode_client(review.author),
            parent_order_id=review.order_id
        )
