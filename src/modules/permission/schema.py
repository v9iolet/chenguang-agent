from pydantic import BaseModel


class PermissionCreate(BaseModel):
    code: str          # 权限标识，如 "user:list"
    name: str          # 权限名称，如 "用户列表"
    description: str | None = None  # 权限描述

class PermissionUpdate(BaseModel):
    name: str | None
    description: str | None
    # code 不允许修改

class PermissionRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    model_config = {"from_attributes": True}