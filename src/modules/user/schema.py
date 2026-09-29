from pydantic import BaseModel, EmailStr  # EmailStr 会自动校验邮箱格式是否合法

from src.modules.role.schema import RoleRead

"""
数据校验层（schema.py）
=================================================
作用：定义"接口收发数据"的格式，用的是 Pydantic。
和 model.py 的区别：
- model.py 管"数据库里的数据长什么样"；
- schema.py 管"前端传给后端、后端返回给前端的数据长什么样"。
例如：创建用户时要接收密码，但返回给前端时不能带密码——靠不同的 schema 来区分。
"""
class UserCreate(BaseModel):
    """创建用户时的入参格式（前端 -> 后端）"""

    username: str       # 用户名
    email: EmailStr     # 邮箱（格式不合法会被 Pydantic 直接拦下，返回 422 错误）
    password: str       # 明文密码（仅注册时接收，入库前应加密）


class UserRead(BaseModel):
    """返回用户信息时的出参格式（后端 -> 前端），故意不含密码，避免泄露"""

    id: int             # 用户 id
    username: str       # 用户名
    email: str          # 邮箱
    is_active: bool     # 是否启用

    # 开启 from_attributes 后，可以直接读取 ORM 对象（model.py 里的 User）的属性，
    # 这样 UserRead.model_validate(user) 就能把数据库对象转成接口返回格式
    model_config = {"from_attributes": True}

class UserWithRolesRead(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    roles: list[RoleRead] = []     # 从 role 模块导入 RoleRead
    model_config = {"from_attributes": True}

class UserAssignRoles(BaseModel):
    role_ids: list[int]