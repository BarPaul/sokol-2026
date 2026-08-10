"""Seed demo data: articles and knowledge documents for development."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import select

from app.db.session import Base, SessionLocal, engine
from app.models.account import Account
from app.models.article import Article
from app.models.knowledge import KnowledgeDocument
from app.services.knowledge.knowledge_service import KnowledgeService


def init_db():
    Base.metadata.create_all(bind=engine)
    from app.services.knowledge.knowledge_service import KnowledgeService

    db = SessionLocal()
    try:
        KnowledgeService(db).ensure_fts()
    finally:
        db.close()


def seed():
    from sqlalchemy import select

    from app.models.account import Account, Role
    from app.services.auth.auth_service import hash_password
    from app.core.config import settings

    db = SessionLocal()
    try:
        roles = {}
        for name in ("moderator", "editor"):
            role = db.scalar(select(Role).where(Role.name == name))
            if role is None:
                role = Role(name=name)
                db.add(role)
                db.flush()
            roles[name] = role
        db.commit()
        for email, password, first, last, role_name in [
            (settings.seed_admin_email, settings.seed_admin_password, "Администратор", "Системы", "moderator"),
            (settings.seed_editor_email, settings.seed_editor_password, "Редактор", "СтудСемья", "editor"),
        ]:
            if db.scalar(select(Account).where(Account.email == email)) is None:
                db.add(
                    Account(
                        first_name=first,
                        last_name=last,
                        email=email,
                        password_hash=hash_password(password),
                        role_id=roles[role_name].id,
                        status="active",
                        is_active=True,
                    )
                )
        db.commit()
    finally:
        db.close()


DEMO_ARTICLES = [
    {
        "title": "Ежемесячное пособие студенческим семьям",
        "slug": "posobie-studencheskim-semyam",
        "summary": "Какие выплаты положены семьям, где оба родителя учатся очно, и как их оформить.",
        "content": (
            "Студенческая семья может претендовать на ежемесячную денежную выплату, "
            "если оба супруга обучаются очно в аккредитованных образовательных организациях.\n\n"
            "## Кому положено\n"
            "Обоим родителям не исполнилось 35 лет, брак официально зарегистрирован, "
            "супруги не получают аналогичную выплату по другим основаниям.\n\n"
            "## Необходимые документы\n"
            "Паспорта супругов, свидетельство о браке, справки об очном обучении, "
            "заявление в органах социальной защиты."
        ),
        "audience": "Обоим родителям не исполнилось 35 лет, брак официально зарегистрирован, "
            "супруги не получают аналогичную выплату по другим основаниям.",
        "documents": "Паспорта супругов, свидетельство о браке, справки об очном обучении, "
            "заявление в органах социальной защиты.",
        "category": "Выплаты и льготы",
        "region": "Все регионы",
        "official_source": "Законодательство о социальной поддержке студентов",
        "restrictions": "Выплата назначается при условии очного обучения и регистрации брака.",
    },
    {
        "title": "Меры поддержки при рождении ребёнка",
        "slug": "podderzhka-pri-rozhdenii-rebenka",
        "summary": "Единовременные выплаты, материнский капитал и отпуск по уходу для студентов.",
        "content": (
            "При рождении ребёнка — единовременное пособие по беременности и родам, "
            "а также пособие при рождении для социально незащищённых категорий.\n\n"
            "## Кому положено\n"
            "Родителям, являющимся студентами очной формы, при рождении ребёнка.\n\n"
            "## Необходимые документы\n"
            "Свидетельство о рождении, справка об обучении, заявление."
        ),
        "audience": "Родителям, являющимся студентами очной формы, при рождении ребёнка.",
        "documents": "Свидетельство о рождении, справка об обучении, заявление.",
        "category": "Выплаты и льготы",
        "region": "Все регионы",
        "official_source": "Социальный фонд",
        "restrictions": "Для оформления необходимо обратиться в течение установленного срока.",
    },
    {
        "title": "Льготное общежитие для студенческих семей",
        "slug": "lgoty-obshchezhitie-semej",
        "summary": "Приоритетное заселение и пониженная плата за общежитие для семейных пар.",
        "content": (
            "Многие вузы предоставляют преимущественное право на заселение в общежитие "
            "для студенческих семей и сниженную стоимость проживания.\n\n"
            "## Кому положено\n"
            "Семейным парам, где хотя бы один супруг обучается очно в данном вузе.\n\n"
            "## Необходимые документы\n"
            "Свидетельство о браке, справки о зачислении, заявление в деканат."
        ),
        "audience": "Семейным парам, где хотя бы один супруг обучается очно в данном вузе.",
        "documents": "Свидетельство о браке, справки о зачислении, заявление в деканат.",
        "category": "Жильё",
        "region": "Зависит от вуза",
        "official_source": "Положения вузов о студенческом общежитии",
        "restrictions": "Наличие мест и правила конкретного вуза.",
    },
    {
        "title": "Стипендии и повышенные академические стипендии",
        "slug": "stipendii-studencheskim-semyam",
        "summary": "Возможность получать повышенную стипендию при наличии детей.",
        "content": (
            "Студенты, воспитывающие детей, могут претендовать на повышенную "
            "академическую стипендию при условии успеваемости.\n\n"
            "## Кому положено\n"
            "Студентам очной формы, имеющим ребёнка, при отсутствии академических задолженностей.\n\n"
            "## Необходимые документы\n"
            "Свидетельства о рождении детей, справка об успеваемости."
        ),
        "audience": "Студентам очной формы, имеющим ребёнка, при отсутствии академических задолженностей.",
        "documents": "Свидетельства о рождении детей, справка об успеваемости.",
        "category": "Выплаты и льготы",
        "region": "Все регионы",
        "official_source": "Порядок назначения государственной академической стипендии",
        "restrictions": "Наличие академической стипендии и успеваемости.",
    },
    {
        "title": "Бесплатная юридическая консультация для студентов",
        "slug": "besplatnaya-yuridicheskaya-konsultaciya",
        "summary": "Где студенческая семья может получить бесплатную правовую помощь.",
        "content": (
            "Студенческие семьи могут обратиться за бесплатной юридической помощью "
            "в юридические клиники при вузах и государственные консультационные пункты.\n\n"
            "## Кому положено\n"
            "Студентам и членам их семей при обращении в юридическую клинику вуза.\n\n"
            "## Необходимые документы\n"
            "Студенческий билет, паспорт."
        ),
        "audience": "Студентам и членам их семей при обращении в юридическую клинику вуза.",
        "documents": "Студенческий билет, паспорт.",
        "category": "Права и консультации",
        "region": "Все регионы",
        "official_source": "Положения юридических клиник",
        "restrictions": "Бесплатные консультации предоставляются в пределах компетенции клиники.",
    },
]

DEMO_DOCUMENTS = [
    {
        "title": "Какие льготы положены студенческой семье (краткий гид)",
        "content": (
            "Студенческие семьи могут получать: ежемесячное пособие при очном обучении обоих супругов; "
            "единовременные выплаты при рождении ребёнка; приоритетное общежитие; "
            "повышенную стипендию при наличии детей; бесплатную юридическую помощь. "
            "Обращаться следует в социальную защиту, в вуз или в юридическую клинику."
        ),
        "source": "СтудСемья справочник",
        "category": "Выплаты и льготы",
    },
    {
        "title": "Документы для оформления ежемесячного пособия",
        "content": (
            "Для назначения ежемесячного пособия на студенческую семью предоставляются: "
            "паспорта супругов, свидетельство о браке, справки об очном обучении, "
            "справка о составе семьи, заявление в орган социальной защиты."
        ),
        "source": "СтудСемья справочник",
        "category": "Выплаты и льготы",
    },
]


def run():
    init_db()
    seed()
    db = SessionLocal()
    try:
        editor = db.scalar(select(Account).order_by(Account.id).limit(1))
        if not db.scalar(select(Article).limit(1)):
            author = db.scalar(select(Account).where(Account.role.has(name="editor")))
            for item in DEMO_ARTICLES:
                article = Article(
                    title=item["title"],
                    slug=item["slug"],
                    summary=item["summary"],
                    content=item["content"],
                    audience=item.get("audience", ""),
                    documents=item.get("documents", ""),
                    category=item["category"],
                    region=item["region"],
                    official_source=item["official_source"],
                    restrictions=item["restrictions"],
                    status="published",
                    author_id=author.id if author else editor.id,
                )
                db.add(article)
        if not db.scalar(select(KnowledgeDocument).limit(1)):
            for item in DEMO_DOCUMENTS:
                db.add(KnowledgeDocument(**item))
        db.commit()
        KnowledgeService(db).reindex()
        print("Seed data created and knowledge reindexed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()