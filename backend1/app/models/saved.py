from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.base import BaseDocument, utcnow

ApplicationStatus = Literal["saved", "planning", "applied"]


class SavedOpportunity(BaseDocument):
    """A user's saved opportunity, including a full immutable snapshot.

    The snapshot guarantees the user keeps access even if the master
    opportunity record later expires or is deleted.
    """

    userId: str
    originalOpportunityId: str
    savedAt: datetime = Field(default_factory=utcnow)
    notes: str | None = None
    applicationStatus: ApplicationStatus = "saved"
    snapshot: dict = Field(default_factory=dict)
    snapshotMatchScore: int | None = None
    masterDeleted: bool = False
    updatedAt: datetime = Field(default_factory=utcnow)
