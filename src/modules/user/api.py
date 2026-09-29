from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infra.database import get_db                    # 数据库会话依赖：每个请求自动开一个会话，结束自动关闭
from src.core.base_schema import ResponseSchema, PageResult  # 统一响应外壳（形如 {code, message, data}）
from src.modules.user.schema import UserCreate, UserRead, UserWithRolesRead
from src.modules.user.service import UserService
from src.core.deps import get_current_user, PageParams  # 引入依赖注入函数，用于保护接口
from src.modules.user.model import User

"""
接口层（api.py）
=================================================
作用：定义对外暴露的 HTTP 接口（URL、请求方式、参数）。
它是模块最外面的一层，相当于"前台"：
- 接收前端发来的 HTTP 请求；
- 把数据交给 service 层处理；
- 拿到结果后包装成统一的 JSON 格式返回。
自己不写业务逻辑，也不写 SQL。
"""

# 创建路由：本模块所有接口 URL 都以 /users 开头，并归入 "User" 分组（接口文档里更好找）
router = APIRouter(prefix="/users", tags=["User"])

# 依赖注入：每个请求自动创建 UserService 实例，结束自动销毁
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """依赖注入：FastAPI 自动传入数据库会话，再用它创建 UserService"""
    return UserService(db)

# 创建用户接口
@router.post("/", response_model=ResponseSchema[UserRead], summary="创建用户")
async def create_user(
    data: UserCreate,                              # 请求体，FastAPI 自动按 UserCreate 校验字段
    svc: UserService = Depends(get_user_service),  # 自动注入业务逻辑对象
):
    """POST /users —— 创建用户"""
    user = await svc.create_user(data)
    # ORM 对象 -> UserRead 出参格式 -> 套上统一响应外壳返回
    return ResponseSchema(data=UserRead.model_validate(user))

# 获取当前登录用户信息接口
@router.get("/me", response_model=ResponseSchema[UserRead], summary="获取当前登录用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（需要 token）"""
    return ResponseSchema(data=UserRead.model_validate(current_user))

# 查询用户列表接口
@router.get("/search", response_model=ResponseSchema[PageResult[UserRead]], summary="分页查询用户列表")
async def search_users_page(
    params: PageParams = Depends(),
    svc: UserService = Depends(get_user_service),
):
    page_result = await svc.search_users(params)
    # 需要把 ORM 对象转成 Pydantic 对象
    page_result.items = [UserRead.model_validate(u) for u in page_result.items]
    return ResponseSchema(data=page_result)

# 查询用户接口
@router.get("/{user_id}", response_model=ResponseSchema[UserRead], summary="按 id 查询单个用户")
async def get_user(
    user_id: int,                                  # 路径参数：/users/123 会解析为 user_id=123
    svc: UserService = Depends(get_user_service),
):
    """GET /users/{user_id} —— 按 id 查询单个用户"""
    user = await svc.get_user(user_id)
    return ResponseSchema(data=UserRead.model_validate(user))

# 查询用户列表接口
@router.get("/", response_model=ResponseSchema[list[UserRead]], summary="分页查询用户列表")
async def list_users(
    offset: int = 0,                               # 查询参数：?offset=0，跳过的条数
    limit: int = 100,                              # 查询参数：?limit=100，本次取多少条
    svc: UserService = Depends(get_user_service),
):
    """GET /users —— 分页查询用户列表"""
    users = await svc.list_users(offset, limit)
    # 列表中的每个 ORM 对象都要转成 UserRead
    return ResponseSchema(data=[UserRead.model_validate(u) for u in users])

# PUT   /api/v1/users/{user_id}/roles   给用户分配角色
@router.put("/{user_id}/roles", response_model=ResponseSchema[UserRead], summary="给用户分配角色")
async def assign_roles_to_user(
    user_id: int,
    role_ids: list[int],
    svc: UserService = Depends(get_user_service),
):
    user = await svc.assign_roles(user_id, role_ids)
    return ResponseSchema(data=UserRead.model_validate(user))

# GET   /api/v1/users/{user_id}/roles   查看用户的角色列表
@router.get("/{user_id}/roles", response_model=ResponseSchema[list[UserWithRolesRead]], summary="查看用户的角色列表")
async def get_user_roles(
    user_id: int,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user_with_roles(user_id)
    return ResponseSchema(data=[UserWithRolesRead.model_validate(user)])

# DELETE /api/v1/users/{user_id} 删除单个用户
@router.delete("/{user_id}", response_model=ResponseSchema[None], summary="删除单个用户")
async def delete_user(
    user_id: int,
    svc: UserService = Depends(get_user_service),
):
    """DELETE /users/{user_id} —— 根据 id 删除用户"""
    await svc.delete_user(user_id)
    return ResponseSchema(data=None)