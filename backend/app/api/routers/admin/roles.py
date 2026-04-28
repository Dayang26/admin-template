import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.deps import AuditInfo, SessionDep
from app.deps.audit import log_audit
from app.deps.auth import get_current_active_superuser
from app.models.db import Permission, Role, RolePermission
from app.schemas import Response

router = APIRouter(prefix="/admin/roles", tags=["admin/roles"])

# 内置角色，禁止删除
BUILTIN_ROLES = {"superuser", "teacher", "student"}


def _role_to_dict(role: Role, session) -> dict:
    """将角色转为响应字典，包含权限列表。"""
    perms = session.exec(select(Permission).join(RolePermission, RolePermission.permission_id == Permission.id).where(RolePermission.role_id == role.id)).all()
    return {
        "id": str(role.id),
        "name": role.name,
        "description": role.description,
        "is_builtin": role.name in BUILTIN_ROLES,
        "permissions": [{"id": str(p.id), "resource": p.resource, "action": p.action} for p in perms],
    }


@router.get("/", dependencies=[Depends(get_current_active_superuser)])
def get_roles(session: SessionDep) -> Response[list[dict]]:
    """获取所有角色列表，包含权限信息。"""
    roles = session.exec(select(Role).order_by(Role.name)).all()
    return Response.ok(data=[_role_to_dict(r, session) for r in roles])


@router.post("/", dependencies=[Depends(get_current_active_superuser)], status_code=201)
def create_role(
    *,
    session: SessionDep,
    body: dict,
    audit: AuditInfo,
) -> Response[dict]:
    """创建自定义角色。"""
    name = body.get("name", "").strip()
    description = body.get("description", "").strip() or None

    if not name:
        raise HTTPException(status_code=400, detail="角色名称不能为空")
    if len(name) > 50:
        raise HTTPException(status_code=400, detail="角色名称不能超过 50 个字符")

    existing = session.exec(select(Role).where(Role.name == name)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"角色 '{name}' 已存在")

    role = Role(name=name, description=description)
    session.add(role)
    session.commit()
    session.refresh(role)

    log_audit(session, action="创建角色", detail=f"角色: {name}", **audit, status_code=201)

    return Response.ok(data=_role_to_dict(role, session), code=201)


@router.patch("/{role_id}", dependencies=[Depends(get_current_active_superuser)])
def update_role(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    body: dict,
    audit: AuditInfo,
) -> Response[dict]:
    """更新角色信息（名称、描述）。"""
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    name = body.get("name")
    description = body.get("description")

    if name is not None:
        name = name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="角色名称不能为空")
        if name != role.name:
            existing = session.exec(select(Role).where(Role.name == name)).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"角色 '{name}' 已存在")
            role.name = name

    if description is not None:
        role.description = description.strip() or None

    session.add(role)
    session.commit()
    session.refresh(role)

    log_audit(session, action="更新角色", detail=f"角色: {role.name}", **audit)

    return Response.ok(data=_role_to_dict(role, session))


@router.delete("/{role_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_role(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    audit: AuditInfo,
) -> Response[None]:
    """删除角色。内置角色禁止删除。"""
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.name in BUILTIN_ROLES:
        raise HTTPException(status_code=400, detail=f"内置角色 '{role.name}' 不允许删除")

    # 检查是否有用户绑定了该角色
    from app.models.db import UserRole

    user_count = len(session.exec(select(UserRole).where(UserRole.role_id == role_id)).all())
    if user_count > 0:
        raise HTTPException(status_code=400, detail=f"该角色下有 {user_count} 个用户绑定，无法删除")

    role_name = role.name

    # 删除角色权限绑定
    rps = session.exec(select(RolePermission).where(RolePermission.role_id == role_id)).all()
    for rp in rps:
        session.delete(rp)

    session.delete(role)
    session.commit()

    log_audit(session, action="删除角色", detail=f"角色: {role_name}", **audit)

    return Response.ok(data=None)


@router.put("/{role_id}/permissions", dependencies=[Depends(get_current_active_superuser)])
def update_role_permissions(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    body: dict,
    audit: AuditInfo,
) -> Response[dict]:
    """全量替换角色的权限绑定。"""
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    permission_ids: list[str] = body.get("permission_ids", [])

    # 验证所有权限 ID 存在
    permissions = []
    for pid in permission_ids:
        perm = session.get(Permission, uuid.UUID(pid))
        if not perm:
            raise HTTPException(status_code=400, detail=f"权限 ID '{pid}' 不存在")
        permissions.append(perm)

    # 删除旧绑定
    old_rps = session.exec(select(RolePermission).where(RolePermission.role_id == role_id)).all()
    for rp in old_rps:
        session.delete(rp)

    # 创建新绑定
    for perm in permissions:
        session.add(RolePermission(role_id=role_id, permission_id=perm.id))

    session.commit()
    session.refresh(role)

    perm_names = [f"{p.resource}:{p.action}" for p in permissions]
    log_audit(
        session,
        action="更新角色权限",
        detail=f"角色: {role.name}, 权限: {', '.join(perm_names) or '无'}",
        **audit,
    )

    return Response.ok(data=_role_to_dict(role, session))


# ---- 权限列表（只读） ----


@router.get("/permissions", dependencies=[Depends(get_current_active_superuser)])
def get_permissions(session: SessionDep) -> Response[list[dict]]:
    """获取所有权限列表（只读）。"""
    perms = session.exec(select(Permission).order_by(Permission.resource, Permission.action)).all()
    return Response.ok(data=[{"id": str(p.id), "resource": p.resource, "action": p.action} for p in perms])
