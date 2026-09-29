from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base_repository import BaseRepository  # 通用仓储基类（已内置 create/get_by_id/get_all 等）
from src.modules.user.model import User

"""
数据访问层（repository.py）
=================================================
作用：专门和数据库打交道，所有 SQL 查询都写在这一层。
上层（service）只管业务规则，不关心 SQL 怎么写；
以后要改查询语句或换数据库，只动这一层即可。
通用的增删改查已在 BaseRepository 中实现，这里只补充 User 特有的查询。
"""

class UserRepository(BaseRepository[User]):
    """用户表的数据访问类，继承基类后自动拥有基础的增删改查能力"""
    SEARCH_FIELDS = ["username", "email"]
    def __init__(self, db: AsyncSession):
        # 把数据库会话 db 和 User 模型交给父类，父类就知道要操作哪张表
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名查询用户，查不到返回 None"""
        stmt = select(User).where(User.username == username)  # 拼 SQL：SELECT * FROM users WHERE username = ?
        result = await self.db.execute(stmt)                  # 异步执行查询
        return result.scalar_one_or_none()                    # 取第一条：有则返回 User，没有则返回 None

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱查询用户，查不到返回 None（逻辑同上）"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def search_page(self, offset: int, limit: int, keyword: str | None) -> tuple[list[User], int]:
        return await self.get_page(
            offset=offset,
            limit=limit,
            keyword=keyword,
            search_fields=self.SEARCH_FIELDS,
        )
