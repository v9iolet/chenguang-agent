from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import PageResult
from src.core.deps import PageParams
from src.modules.role.repository import RoleRepository
from src.core.exceptions import BizException  # 业务异常：抛出后会被统一转成友好的错误响应
from src.modules.user.model import User
from src.modules.user.schema import UserCreate
from src.modules.user.repository import UserRepository
from src.utils.password_utils import hash_password
"""
业务逻辑层（service.py）
=================================================
作用：处理具体的"业务规则"，是整个模块的大脑。
它夹在 api 层和 repository 层中间：
- 从 api 层拿到请求数据；
- 做校验和判断（比如用户名是否重复）；
- 需要读写数据库时，再调用 repository 层。
这样 api 层只负责收发数据，repository 层只负责 SQL，各管一摊。
"""

class UserService:
    """用户相关的业务逻辑"""

    def __init__(self, db: AsyncSession):
        # service 内部持有一个 repository，真正的数据库操作都交给它
        self.repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def create_user(self, data: UserCreate) -> User:
        """创建用户：先查重，再入库"""
        # 用户名已存在 -> 抛业务异常（code/message 会体现在接口返回中）
        if await self.repo.get_by_username(data.username):
            raise BizException(code=400, message="用户名已存在")
        # 邮箱已存在 -> 同样拒绝
        if await self.repo.get_by_email(data.email):
            raise BizException(code=400, message="邮箱已存在")

        # 校验通过，组装数据库对象
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),  # TODO：目前是明文，正式项目要用 bcrypt 等算法加密后再存
        )
        return await self.repo.create(user)  # 交给仓储层插入，并返回保存后的用户

    async def get_user(self, user_id: int) -> User:
        """根据 id 查询单个用户，不存在就抛 404"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise BizException(code=404, message="用户不存在")
        return user

    async def list_users(self, offset: int = 0, limit: int = 100):
        """分页查询用户列表：offset=跳过多少条，limit=取多少条"""
        return await self.repo.get_all(offset=offset, limit=limit)

    async def assign_roles(self, user_id: int, role_ids: list[int]) -> User:

        # 1. 查找用户，不存在抛异常
        user = await self.get_user(user_id)
        if not user:
            raise BizException(code=400, message="用户不存在")

        # 2. 通过 RoleRepository.get_by_ids(role_ids) 批量查询角色
        role_list = await self.role_repo.get_by_ids(role_ids)

        # 3. 校验数量是否匹配
        if len(role_list) != len(role_ids):
            raise BizException(code=400, message="角色不存在")

        # 4. user.roles = role_list（整体替换）
        user.roles = role_list

        # 5. flush + refresh
        await self.repo.update(user)

        # 6. 返回 user
        return user

    async def get_user_with_roles(self, user_id: int) -> User:
        # 和 get_user 一样，但返回的 User 对象会自动带上 roles
        user = await self.get_user(user_id)
        return user


    async def search_users(self, params: PageParams) -> PageResult[Any]:
        items, total = await self.repo.search_page(
            offset=params.offset,
            limit=params.page_size,
            keyword=params.keyword,
        )
        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def delete_user(self, user_id: int) -> None:
        """根据 id 删除单个用户"""
        user = await self.get_user(user_id)
        await self.repo.delete(user)