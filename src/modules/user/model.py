from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base_model import BaseModel  # 模型公共基类（一般内置 id、创建时间等公共字段）
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from src.modules.role.model import user_roles, Role



"""
模型层（model.py）
=================================================
作用：定义数据库表对应的 Python 类（ORM 模型）。
简单理解：一个类 = 数据库里的一张表，类的属性 = 表的字段。
SQLAlchemy 会根据这个类自动生成 SQL，我们不用手写建表语句。
"""

class User(BaseModel):
    """用户模型，对应数据库中的 users 表"""

    __tablename__ = "users"  # 该模型在数据库里的真实表名

    # 用户名：最长 50 的字符串；unique=不能重复，index=建索引加快查询
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    # 邮箱：最长 100，同样要求唯一并建索引
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="邮箱")
    # 密码哈希：存加密后的密码，绝不存明文，长度预留 255
    hashed_password: Mapped[str] = mapped_column(String(255), comment="密码哈希")
    # 是否启用：布尔值，新建用户默认为启用
    # 新增：用户拥有的角色列表
    roles: Mapped[list["Role"]] = relationship(secondary=user_roles,lazy="selectin")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    is_superuser: Mapped[bool] = mapped_column(default=False, comment="是否为超级管理员")
    last_login: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, comment="最后登录时间")
