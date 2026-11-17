from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.models import Product
class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    async def find_by_category(self, category: str|None=None):
        conditions = [Product.status == "active"]
        if category:
            conditions.append(Product.category == category)
        # 2.查询产品列表
        products = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(Product.id.asc())
        )
        return products.all()
