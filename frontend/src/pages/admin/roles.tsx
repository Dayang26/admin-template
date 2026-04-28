import { useState } from 'react'
import { Plus, Trash2, Pencil, Shield, ShieldCheck } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { PageHeader } from '@/components/shared/page-header'
import { ConfirmDialog } from '@/components/shared/confirm-dialog'
import {
  useRoles,
  usePermissions,
  useCreateRole,
  useUpdateRole,
  useDeleteRole,
  useUpdateRolePermissions,
} from '@/lib/hooks/use-roles'
import { getRoleLabel } from '@/lib/utils/role-labels'
import {
  formatAggregatedPermissions,
  groupPermissionsByResource,
  getResourceLabel,
  getActionLabel,
} from '@/lib/utils/permission-labels'
import type { RoleItem } from '@/lib/types/role'

export function RolesPage() {
  const { data: roles, isLoading } = useRoles()
  const { data: allPermissions } = usePermissions()
  const createMutation = useCreateRole()
  const updateMutation = useUpdateRole()
  const deleteMutation = useDeleteRole()
  const updatePermsMutation = useUpdateRolePermissions()

  const [createOpen, setCreateOpen] = useState(false)
  const [editRole, setEditRole] = useState<RoleItem | null>(null)
  const [permsRole, setPermsRole] = useState<RoleItem | null>(null)
  const [deleteRole, setDeleteRole] = useState<RoleItem | null>(null)

  // 创建角色表单
  const [newName, setNewName] = useState('')
  const [newDesc, setNewDesc] = useState('')

  // 编辑角色表单
  const [editName, setEditName] = useState('')
  const [editDesc, setEditDesc] = useState('')

  // 权限编辑
  const [selectedPermIds, setSelectedPermIds] = useState<Set<string>>(new Set())

  function handleCreate() {
    if (!newName.trim()) return
    createMutation.mutate(
      { name: newName.trim(), description: newDesc.trim() || undefined },
      {
        onSuccess: () => {
          toast.success('角色创建成功')
          setCreateOpen(false)
          setNewName('')
          setNewDesc('')
        },
        onError: (err) => toast.error(err instanceof Error ? err.message : '创建失败'),
      },
    )
  }

  function handleUpdate() {
    if (!editRole || !editName.trim()) return
    updateMutation.mutate(
      { roleId: editRole.id, data: { name: editName.trim(), description: editDesc.trim() || undefined } },
      {
        onSuccess: () => {
          toast.success('角色已更新')
          setEditRole(null)
        },
        onError: (err) => toast.error(err instanceof Error ? err.message : '更新失败'),
      },
    )
  }

  function handleDelete() {
    if (!deleteRole) return
    deleteMutation.mutate(deleteRole.id, {
      onSuccess: () => {
        toast.success('角色已删除')
        setDeleteRole(null)
      },
      onError: (err) => toast.error(err instanceof Error ? err.message : '删除失败'),
    })
  }

  function openPermsDialog(role: RoleItem) {
    setPermsRole(role)
    setSelectedPermIds(new Set(role.permissions.map((p) => p.id)))
  }

  function togglePerm(permId: string) {
    setSelectedPermIds((prev) => {
      const next = new Set(prev)
      if (next.has(permId)) {
        next.delete(permId)
      } else {
        next.add(permId)
      }
      return next
    })
  }

  function handleSavePerms() {
    if (!permsRole) return
    updatePermsMutation.mutate(
      { roleId: permsRole.id, permissionIds: Array.from(selectedPermIds) },
      {
        onSuccess: () => {
          toast.success('权限已更新')
          setPermsRole(null)
        },
        onError: (err) => toast.error(err instanceof Error ? err.message : '更新失败'),
      },
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="角色管理"
        description="管理系统角色和权限分配"
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            创建角色
          </Button>
        }
      />

      {/* 角色卡片列表 */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardHeader><Skeleton className="h-5 w-24" /></CardHeader>
              <CardContent><Skeleton className="h-4 w-48" /></CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {roles?.map((role) => (
            <Card key={role.id}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  {role.is_builtin ? (
                    <ShieldCheck className="h-4 w-4 text-primary" />
                  ) : (
                    <Shield className="h-4 w-4 text-muted-foreground" />
                  )}
                  {getRoleLabel(role.name)}
                </CardTitle>
                {role.is_builtin && (
                  <Badge variant="secondary">内置</Badge>
                )}
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  {role.description ?? '暂无描述'}
                </p>

                {/* 权限标签 */}
                <div className="flex flex-wrap gap-1">
                  {role.permissions.length === 0 ? (
                    <span className="text-xs text-muted-foreground">无权限</span>
                  ) : (
                    formatAggregatedPermissions(role.permissions).map((label, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {label}
                      </Badge>
                    ))
                  )}
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setEditRole(role)
                      setEditName(role.name)
                      setEditDesc(role.description ?? '')
                    }}
                  >
                    <Pencil className="mr-1 h-3 w-3" />
                    编辑
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openPermsDialog(role)}
                  >
                    <Shield className="mr-1 h-3 w-3" />
                    权限
                  </Button>
                  {!role.is_builtin && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteRole(role)}
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 创建角色弹窗 */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>创建角色</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>角色名称 *</Label>
              <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="如：assistant" />
            </div>
            <div className="space-y-2">
              <Label>描述</Label>
              <Input value={newDesc} onChange={(e) => setNewDesc(e.target.value)} placeholder="可选" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>取消</Button>
            <Button disabled={!newName.trim() || createMutation.isPending} onClick={handleCreate}>
              {createMutation.isPending ? '创建中...' : '创建'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑角色弹窗 */}
      <Dialog open={!!editRole} onOpenChange={(open) => !open && setEditRole(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>编辑角色</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>角色名称</Label>
              <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>描述</Label>
              <Input value={editDesc} onChange={(e) => setEditDesc(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditRole(null)}>取消</Button>
            <Button disabled={!editName.trim() || updateMutation.isPending} onClick={handleUpdate}>
              {updateMutation.isPending ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 权限编辑弹窗 */}
      <Dialog open={!!permsRole} onOpenChange={(open) => !open && setPermsRole(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              编辑权限 — {permsRole ? getRoleLabel(permsRole.name) : ''}
            </DialogTitle>
          </DialogHeader>
          <div className="max-h-[60vh] overflow-y-auto space-y-6 pr-2">
            {allPermissions && Object.entries(groupPermissionsByResource(allPermissions)).map(([resource, perms]) => (
              <div key={resource} className="space-y-3">
                <h4 className="text-sm font-semibold text-foreground border-b pb-1">
                  {getResourceLabel(resource)}
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {perms.map((perm) => {
                    const checked = selectedPermIds.has(perm.id)
                    return (
                      <button
                        key={perm.id}
                        type="button"
                        onClick={() => togglePerm(perm.id)}
                        className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors border ${
                          checked ? 'bg-primary/10 text-primary border-primary/20' : 'hover:bg-accent border-transparent'
                        }`}
                      >
                        <div className={`h-4 w-4 rounded border flex items-center justify-center shrink-0 ${
                          checked ? 'bg-primary border-primary' : 'border-input bg-background'
                        }`}>
                          {checked && <span className="text-primary-foreground text-xs leading-none">✓</span>}
                        </div>
                        <span>{getActionLabel(perm.action)}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPermsRole(null)}>取消</Button>
            <Button disabled={updatePermsMutation.isPending} onClick={handleSavePerms}>
              {updatePermsMutation.isPending ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认 */}
      <ConfirmDialog
        open={!!deleteRole}
        onOpenChange={(open) => !open && setDeleteRole(null)}
        title="确认删除"
        description={`确定要删除角色"${deleteRole?.name ?? ''}"吗？此操作不可撤销。`}
        confirmLabel="删除"
        variant="destructive"
        loading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  )
}
