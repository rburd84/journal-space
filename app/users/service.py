from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.users.clerk import get_verified_clerk_email
from app.users.invitations import InvitationModel
from app.users.models import UserModel


def resolve_current_user(
        session: Session,
        clerk_user_id: str,
) -> UserModel:
    # First, look for an existing Stillspace account.
    user = session.scalar(
        select(UserModel).where(
            UserModel.clerk_user_id == clerk_user_id
        )
    )

    if user is not None:
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Account disabled",
            )

        return user

    # New users must have a verified Clerk email.
    email = get_verified_clerk_email(clerk_user_id)

    invitation = session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == email
        )
    )

    # Only pending, non-revoked invitations can be redeemed.
    if (
            invitation is None
            or invitation.revoked_at is not None
            or invitation.redeemed_at is not None
            or invitation.redeemed_by_user_id is not None
    ):
        raise HTTPException(
            status_code=403,
            detail="Access not authorized",
        )

    try:
        # Create the internal Stillspace user.
        user = UserModel(
            clerk_user_id=clerk_user_id,
        )

        session.add(user)
        session.flush()

        # Claim the invitation only if it is still available.
        result = session.execute(
            update(InvitationModel)
            .where(
                InvitationModel.id == invitation.id,
                InvitationModel.revoked_at.is_(None),
                InvitationModel.redeemed_at.is_(None),
                InvitationModel.redeemed_by_user_id.is_(None),
            )
            .values(
                redeemed_at=datetime.now(timezone.utc),
                redeemed_by_user_id=user.id,
            )
            .execution_options(synchronize_session=False)
        )

        if result.rowcount != 1:
            session.rollback()

            raise HTTPException(
                status_code=403,
                detail="Invitation already used",
            )

        # Both changes succeed or fail together.
        session.commit()
        session.refresh(user)

        return user

    except IntegrityError as error:
        session.rollback()

        raise HTTPException(
            status_code=403,
            detail="Access not authorized",
        ) from error
