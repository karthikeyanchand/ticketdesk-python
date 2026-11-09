"""Create two demo organizations with users and tickets.

    python seed.py
"""
from ticketdesk.database import SessionLocal, init_db
from ticketdesk.models import (Comment, Organization, Role, Ticket, TicketPriority, User)
from ticketdesk.security import hash_password

DEMO_PASSWORD = "correct-horse-battery"

ORGS = {
    "acme": [("admin@acme.example.com", "Ada Admin", Role.ADMIN), ("agent@acme.example.com", "Alan Agent", Role.AGENT),
             ("cust@acme.example.com", "Cara Customer", Role.CUSTOMER)],
    "globex": [("admin@globex.example.com", "Gus Admin", Role.ADMIN), ("agent@globex.example.com", "Gail Agent", Role.AGENT),
               ("cust@globex.example.com", "Gene Customer", Role.CUSTOMER)],
}


def main() -> None:
    init_db()
    with SessionLocal() as db:
        if db.query(Organization).count():
            print("already seeded")
            return
        for slug, people in ORGS.items():
            org = Organization(name=slug.title(), slug=slug)
            db.add(org)
            db.flush()
            users = []
            for email, name, role in people:
                u = User(org_id=org.id, email=email, full_name=name, role=role,
                         password_hash=hash_password(DEMO_PASSWORD))
                db.add(u)
                users.append(u)
            db.flush()
            admin_u, agent_u, cust_u = users
            for i, subject in enumerate(["Cannot log in", "Invoice is wrong", "Feature request: dark mode"], 1):
                t = Ticket(org_id=org.id, subject=f"{subject} ({slug})", description=f"Details for {subject}",
                           priority=TicketPriority.HIGH if i == 1 else TicketPriority.NORMAL,
                           requester_id=cust_u.id, assignee_id=agent_u.id)
                db.add(t)
                db.flush()
                db.add(Comment(ticket_id=t.id, author_id=agent_u.id, body="Thanks, looking into it."))
                db.add(Comment(ticket_id=t.id, author_id=agent_u.id, body="Internal: check billing logs",
                               internal=True))
        db.commit()
    print(f"seeded 2 orgs; every demo user's password is {DEMO_PASSWORD!r}")


if __name__ == "__main__":
    main()
