from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, search: str = "") -> list[dict]:
        stmt = select(Category).order_by(Category.sort_order, Category.name)
        if search:
            stmt = stmt.where(Category.name.ilike(f"%{search}%"))
        categories = list(self.db.scalars(stmt))
        counts = dict(
            self.db.execute(
                select(Article.category, func.count(Article.id))
                .where(Article.status == "published")
                .group_by(Article.category)
            ).all()
        )
        return [
            {
                "id": c.id,
                "name": c.name,
                "sort_order": c.sort_order,
                "created_at": c.created_at,
                "count": counts.get(c.name, 0),
            }
            for c in categories
        ]

    def get(self, category_id: int) -> Category:
        cat = self.db.get(Category, category_id)
        if cat is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        return cat

    def create(self, payload: CategoryCreate) -> Category:
        name = payload.name.strip()
        if self.db.scalar(select(Category).where(Category.name == name)):
            raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")
        cat = Category(name=name, sort_order=payload.sort_order)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def update(self, category_id: int, payload: CategoryUpdate) -> Category:
        cat = self.get(category_id)
        changes = payload.model_dump(exclude_unset=True)
        if "name" in changes and changes["name"]:
            new_name = changes["name"].strip()
            existing = self.db.scalar(select(Category).where(Category.name == new_name, Category.id != category_id))
            if existing:
                raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")
            cat.name = new_name
        if "sort_order" in changes:
            cat.sort_order = changes["sort_order"]
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def delete(self, category_id: int) -> None:
        cat = self.get(category_id)
        articles_count = self.db.scalar(
            select(func.count(Article.id)).where(Article.category == cat.name)
        )
        if articles_count:
            raise HTTPException(status_code=400, detail="Нельзя удалить категорию, в которой есть статьи")
        self.db.delete(cat)
        self.db.commit()