import asyncio
from sqlalchemy import select
from src.infra.database import AsyncSessionLocal
from src.modules.permission.model import Permission
from src.modules.role.model import Role
from src.modules.user.model import User
from src.utils.password_utils import hash_password

INITIAL_PERMISSIONS = [
    # 用户管理
    {"code": "user:read", "name": "查看用户", "description": "查看用户列表及详情"},
    {"code": "user:create", "name": "创建用户", "description": "新增系统用户账号"},
    {"code": "user:update", "name": "编辑用户", "description": "修改用户信息及角色分配"},
    {"code": "user:delete", "name": "删除用户", "description": "删除或停用系统用户"},

    # 角色管理
    {"code": "role:read", "name": "查看角色", "description": "查看角色列表及权限"},
    {"code": "role:create", "name": "创建角色", "description": "新增系统角色"},
    {"code": "role:update", "name": "编辑角色", "description": "修改角色信息及权限配置"},
    {"code": "role:delete", "name": "删除角色", "description": "删除系统角色"},

    # 权限管理
    {"code": "permission:read", "name": "查看权限", "description": "查看权限列表"},
    {"code": "permission:create", "name": "创建权限", "description": "定义新权限"},
    {"code": "permission:update", "name": "编辑权限", "description": "修改权限定义"},
    {"code": "permission:delete", "name": "删除权限", "description": "删除权限定义"},

    # Agent管理
    {"code": "agent:read", "name": "查看Agent", "description": "查看智能体列表及详情"},
    {"code": "agent:create", "name": "创建Agent", "description": "新建智能体"},
    {"code": "agent:update", "name": "编辑Agent", "description": "配置与调试智能体"},
    {"code": "agent:delete", "name": "删除Agent", "description": "删除智能体"},

    # 模型管理
    {"code": "model:read", "name": "查看模型", "description": "查看大语言模型列表"},
    {"code": "model:create", "name": "接入模型", "description": "添加新模型配置"},

    # 知识库管理
    {"code": "knowledge:read", "name": "查看知识库", "description": "查看RAG知识库列表"},
    {"code": "knowledge:create", "name": "创建知识库", "description": "新建RAG知识库并上传文档"},

    # 工具管理
    {"code": "tool:read", "name": "查看工具", "description": "查看可用工具列表"},
    {"code": "tool:create", "name": "注册工具", "description": "注册外部API工具"},
]

INITIAL_ROLES = [
    {
        "code": "admin",
        "name": "超级管理员",
        "description": "拥有系统所有功能与最高管控权限",
        "all_perms": True,
    },
    {
        "code": "developer",
        "name": "开发者",
        "description": "负责模型接入、Agent创建与开发测试",
        "perm_prefixes": ["agent:", "model:", "knowledge:", "tool:"],
    },
    {
        "code": "operator",
        "name": "运营人员",
        "description": "日常对话日志分析、效果监控与基本管理",
        "perm_prefixes": ["agent:read", "knowledge:read", "user:read"],
    },
    {
        "code": "viewer",
        "name": "访客",
        "description": "仅具备基本浏览与体验权限",
        "perm_prefixes": [":read"],
    },
]

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("1. 正在初始化权限数据...")
        perm_map = {}
        for p in INITIAL_PERMISSIONS:
            stmt = select(Permission).where(Permission.code == p["code"])
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if not existing:
                existing = Permission(
                    code=p["code"],
                    name=p["name"],
                    description=p["description"]
                )
                session.add(existing)
                await session.flush()
                await session.refresh(existing)
                print(f"  + 权限已创建: {existing.code} ({existing.name})")
            perm_map[existing.code] = existing

        print("2. 正在初始化角色数据...")
        role_map = {}
        for r in INITIAL_ROLES:
            stmt = select(Role).where(Role.code == r["code"])
            existing_role = (await session.execute(stmt)).scalar_one_or_none()
            if not existing_role:
                existing_role = Role(
                    code=r["code"],
                    name=r["name"],
                    description=r["description"]
                )
                session.add(existing_role)
                await session.flush()
                await session.refresh(existing_role)
                print(f"  + 角色已创建: {existing_role.code} ({existing_role.name})")

            # 关联权限
            if r.get("all_perms"):
                existing_role.permissions = list(perm_map.values())
            elif r.get("perm_prefixes"):
                prefixes = r["perm_prefixes"]
                assigned = [
                    p for code, p in perm_map.items()
                    if any(code.startswith(pref) or pref in code for pref in prefixes)
                ]
                existing_role.permissions = assigned
            session.add(existing_role)
            await session.flush()
            role_map[existing_role.code] = existing_role

        print("3. 正在初始化超级管理员账号...")
        admin_stmt = select(User).where(User.username == "admin")
        admin_user = (await session.execute(admin_stmt)).scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_superuser=True,
                roles=[role_map["admin"]]
            )
            session.add(admin_user)
            await session.flush()
            print("  + 超级管理员账号创建成功！用户名: admin，密码: admin123")
        else:
            print("  * 超级管理员账号已存在")

        await session.commit()
        print("初始化数据库种子数据完成！")

if __name__ == "__main__":
    asyncio.run(seed_data())
