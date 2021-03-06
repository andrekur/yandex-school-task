from sqlalchemy import (
    Column, ForeignKey,
    Integer, String,
    DateTime, UniqueConstraint,
    BigInteger, Index
)
from .connector import Base


class CategoryModel(Base):
    """
    Category model in db
    """
    __tablename__ = 'category'

    id = Column(String(length=36), primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(BigInteger, nullable=True)
    date = Column(DateTime, nullable=False)


class ProductModel(Base):
    """
    Product model in db
    """
    __tablename__ = 'product'

    id = Column(String(length=36), primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(BigInteger, nullable=False)
    date = Column(DateTime, nullable=False)
    parentId = Column(
        String(length=36),
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )


class CategoriesRelationsModel(Base):
    """
    Category-relations model in db
    """
    __tablename__ = 'category_relations'
    __table_args__ = (
        UniqueConstraint(
            'parent_id', 'children_id'
        ),
        Index(
            'category_relation_index_parent_id_children_id',
            'parent_id',
            'children_id'
        )
    )
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(
        String(length=36),
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    children_id = Column(
        String(length=36),
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
