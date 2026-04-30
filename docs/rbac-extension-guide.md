# RBAC 扩展指南 (业务模块开发规范)

本项目使用高度解耦的基于资源的**全局角色访问控制 (RBAC)** 模型。当您需要向后台系统新增一个业务模块（例如：商品管理、订单管理、文章管理）时，请严格按照以下 6 步标准流程操作，以确保前后端权限一致。

本指南以新增一个 **文章管理 (Article)** 模块为例。

---

## Step 1: 声明权限种子数据 (Backend)

系统每次启动时会自动同步默认权限。您必须首先在数据库初始化脚本中声明新的操作权限点。

打开 `backend/app/core/db.py`，找到 `BUILTIN_PERMISSIONS` 列表，追加对于 `article` 资源的操作：

```python
BUILTIN_PERMISSIONS = [
    # ... 已有的 user, role 等资源权限
    
    # 新增的文章模块权限
    {"resource": "article", "action": "create"},
    {"resource": "article", "action": "read"},
    {"resource": "article", "action": "update"},
    {"resource": "article", "action": "delete"},
]
```

如果需要让默认的某些角色自带此权限，可以在下方的 `ROLE_PERMISSION_MAP` 进行绑定（注意：`superuser` 会自动接管所有权限，不用手动绑定）。

---

## Step 2: 建立数据模型与 Schema (Backend)

在定义接口之前，先完成底层模型映射。

### 1. 数据库 Model (`models/db`)
新建 `backend/app/models/db/article.py`:
```python
import uuid
from sqlmodel import Field
from app.models.db.base import UUIDPrimaryKeyMixin, TimestampMixin

class Article(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "t_article"
    title: str = Field(max_length=255)
    content: str | None = Field(default=None)
```
> **关键点**：在 `backend/app/models/db/__init__.py` 中导入新建的模型，否则 Alembic 将无法识别到它的存在。

### 2. Schema 模型 (`schemas`)
新建 `backend/app/schemas/article.py`:
```python
from sqlmodel import SQLModel

class ArticleCreateReq(SQLModel):
    title: str
    content: str | None = None
```

---

## Step 3: 生成数据库迁移脚本 (Backend)

运行我们统一包装好的指令：

```bash
make db-revision
```

这会自动在 `backend/app/alembic/versions/` 目录下生成一个新的 Python 迁移脚本。
> **注意**：自动生成可能会遗漏 SQLModel 的导入。打开生成的文件，如果看到类似 `sa.Column`，确保在顶部加一句 `import sqlmodel`。

确认无误后执行表结构升级：
```bash
make db-upgrade
```

---

## Step 4: 编写接口与鉴权拦截 (Backend)

### 1. Router 层 (`api/routers`)
新建 `backend/app/api/routers/admin/articles.py`，并务必在入口处挂载 `require_permission` 依赖：

```python
import uuid

from fastapi import APIRouter, Depends

from app.deps import AuditInfo, SessionDep
from app.deps.audit import log_audit
from app.deps.permission import require_permission
from app.schemas import Response
from app.schemas.article import ArticleCreateReq, ArticlePublicResp
from app.services import article_service

router = APIRouter()


@router.post(
    "/",
    dependencies=[Depends(require_permission("article", "create"))],
    response_model=Response[ArticlePublicResp],
    status_code=201,
)
def create_article(
    *,
    session: SessionDep,
    article_in: ArticleCreateReq,
    audit: AuditInfo,
) -> Response[ArticlePublicResp]:
    article = article_service.create_article(session=session, article_in=article_in)
    log_audit(
        session,
        action="创建文章",
        detail=f"标题: {article.title}",
        **audit,
        status_code=201,
    )
    return Response.ok(data=ArticlePublicResp.model_validate(article), code=201)
```

### 2. 挂载至主路由
在 `backend/app/api/main.py` 中引入并挂载：
```python
from app.api.routers.admin import articles

api_router.include_router(articles.router, prefix="/admin/articles", tags=["Admin Articles"])
```

### 3. 操作审计日志（可选但推荐）
针对所有的“增删改”操作，强烈建议接入审计依赖 `log_audit`：
```python
from app.deps import AuditInfo, SessionDep
from app.deps.audit import log_audit

@router.delete(
    "/{article_id}",
    dependencies=[Depends(require_permission("article", "delete"))],
    response_model=Response[None],
)
def delete_article(
    article_id: uuid.UUID,
    session: SessionDep,
    audit: AuditInfo,
) -> Response[None]:
    article_service.delete_article(session=session, article_id=article_id)
    log_audit(session, action="删除文章", detail=f"文章ID: {article_id}", **audit)
    return Response.ok(data=None, message="文章已删除")
```

---

## Step 5: 前端对接与路由设置 (Frontend)

### 1. 添加权限名称映射字典
为了让“系统管理 -> 角色管理”的配置界面能以中文友好的形式显示您的新权限，请去 `frontend/src/lib/utils/permission-labels.ts` 补充映射：
```typescript
export const RESOURCE_LABELS: Record<string, string> = {
  // ... 其他资源
  article: '文章管理',
}
```

### 2. 创建页面组件与路由 (`pages`, `router.tsx`)
在 `frontend/src/pages/admin/articles` 编写您的增删改查 UI，随后在 `src/router.tsx` 中注册：

```tsx
import { RequireAuth } from '@/lib/auth/guard'

// ...
{
  path: 'articles',
  // 组件级别的安全兜底：如果用户直达 URL 但无权限，渲染拦截 UI
  element: <RequireAuth permissions={['article:read']}><ArticlePage /></RequireAuth>,
}
```

### 3. 配置侧边栏入口 (`components/layout/admin-sidebar.tsx`)
让具备权限的用户看到新菜单：
```tsx
const adminNavigation = [
  // ...
  {
    title: '文章管理',
    url: '/admin/articles',
    icon: FileText,           // 您的菜单图标
    permissions: ['article:read'], // 【核心管控】如果用户无此权限，菜单将在渲染时被自动隐藏
  },
]
```

---

## Step 6: 编写单元测试与上线 (Testing)

最后一步，编写防线保障！
在 `backend/tests/api/admin/` 建立 `test_articles.py`，必须覆盖两类核心鉴权场景：
1. **白盒授权测试**：携带授权（拥有 `superuser` 或是手动创建并绑定了含有 `article:xx` 的角色的账号）访问接口，断言返回 `200`。
2. **越权拦截测试 (Enforcement Test)**：构造一个**不包含**该接口所需权限角色的普通用户，尝试请求 API，断言后端必定拦截并返回 HTTP `403 Forbidden`。

完成这两类测试用例编写，且 `make test` 验证通过后，您的新业务模块就完美融合进了当前模板底座之中！
