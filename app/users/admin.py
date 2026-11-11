import argparse
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.users.invitations import InvitationModel
from app.users.models import UserModel  # noqa: F401


def normalize_email(email: str) -> str:
    email = email.strip().lower()

    if (
            not email
            or email.count("@") != 1
            or any(char.isspace() for char in email)
    ):
        raise ValueError("Invalid email address")

    local, domain = email.split("@")

    if not local or not domain or "." not in domain:
        raise ValueError("Invalid email address")

    if len(email) > 320:
        raise ValueError("Email address is too long")

    return email


def invite(session: Session, email: str) -> str:
    email = normalize_email(email)

    invitation = session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == email
        )
    )

    if invitation:
        if invitation.redeemed_at is not None:
            return "Invitation already redeemed"

        if invitation.revoked_at is None:
            return "Invitation already exists"

        invitation.revoked_at = None
        session.commit()
        return f"Invitation restored: {email}"

    session.add(InvitationModel(email=email))
    session.commit()

    return f"Invitation created: {email}"


def revoke(session: Session, email: str) -> str:
    email = normalize_email(email)

    invitation = session.scalar(
        select(InvitationModel).where(
            InvitationModel.email == email
        )
    )

    if invitation is None:
        return "Invitation not found"

    if invitation.redeemed_at is not None:
        return (
            "Invitation already redeemed. "
            "Disable the user account to revoke access."
        )

    if invitation.revoked_at is not None:
        return "Invitation already revoked"

    invitation.revoked_at = datetime.now(timezone.utc)
    session.commit()

    return f"Invitation revoked: {email}"


def list_invitations(session: Session) -> list[str]:
    invitations = session.scalars(
        select(InvitationModel).order_by(InvitationModel.email)
    ).all()

    results = []

    for invitation in invitations:
        if invitation.revoked_at is not None:
            status = "revoked"
        elif invitation.redeemed_at is not None:
            status = "redeemed"
        else:
            status = "pending"

        results.append(f"{invitation.email} | {status}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage Stillspace invitations"
    )

    parser.add_argument(
        "action",
        choices=["invite", "list", "revoke"],
    )

    parser.add_argument(
        "email",
        nargs="?",
    )

    args = parser.parse_args()

    if args.action in {"invite", "revoke"} and not args.email:
        parser.error("An email address is required")

    if args.action == "list" and args.email:
        parser.error("The list command does not accept an email")

    try:
        with SessionLocal() as session:
            if args.action == "invite":
                print(invite(session, args.email))
            elif args.action == "revoke":
                print(revoke(session, args.email))
            else:
                for item in list_invitations(session):
                    print(item)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
