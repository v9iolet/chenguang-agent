from typing import TypeVar, Generic, Type, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base_model import BaseModel
from sqlalchemy import select, func, or_, String
from sqlalchemy.orm import InspectionAttr

# 定义泛型类型变量 T，约束其必须为 BaseModel 或其子类
T = TypeVar("T", bound=BaseModel)


# 泛型仓储基类，为各数据模型提供统一的 CRUD 基础操作
class BaseRepository(Generic[T]):
    # 构造时绑定具体的模型类，并注入异步数据库会话
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    # 按主键 id 查询单条记录，不存在时返回 None
    async def get_by_id(self, id: int) -> T | None:
        return await self.db.get(self.model, id)

    # 分页查询记录列表，offset 为偏移量，limit 为返回条数上限
    async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # 新增记录：加入会话后刷盘并刷新，返回含数据库生成字段的对象
    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    # 更新记录：刷盘提交修改并刷新对象，返回最新数据
    async def update(self, obj: T) -> T:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    # 删除指定对象对应的数据库记录并刷盘执行
    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    # 删除指定主键 id 对应的记录并刷盘执行
    async def delete_by_id(self, id: int) -> bool:
        obj = await self.get_by_id(id)
        if obj is not None:
            await self.db.delete(obj)
            await self.db.flush()
            return True
        return False

    async def get_page(
            self,
            offset: int = 0,
            limit: int = 20,
            keyword: str | None = None,
            search_fields: list[str] | None = None,
    ) -> tuple[list[T], int]:
        """
        通用分页 + 模糊搜索

        参数：
            offset: 偏移量
            limit: 每页条数
            keyword: 搜索关键词
            search_fields: 要搜索的字段名列表，如 ["username", "email"]

        返回：
            (数据列表, 总条数) 的元组
        """
        stmt = select(self.model)

        # 如果有关键词且指定了搜索字段，构建 OR 模糊查询
        if keyword and search_fields:
            conditions = []
            for field_name in search_fields:
                column = getattr(self.model, field_name, None)
                if column is not None:
                    conditions.append(column.like(f"%{keyword}%"))
            if conditions:
                stmt = stmt.where(or_(*conditions))

        # 查询总数（复用相同的 WHERE 条件）
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # 查询分页数据
        stmt = stmt.offset(offset).limit(limit).order_by(self.model.id.desc())
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total