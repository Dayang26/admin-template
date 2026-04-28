import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Trash2, UserPlus, Search, Check } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PageHeader } from '@/components/shared/page-header'
import { ConfirmDialog } from '@/components/shared/confirm-dialog'
import {
  useClassDetail,
  useUpdateClass,
  useClassMembers,
  useAddClassMember,
  useRemoveClassMember,
} from '@/lib/hooks/use-classes'
import { useUsers } from '@/lib/hooks/use-users'
import { useDebounce } from '@/lib/hooks/use-debounce'
import type { UserPublic } from '@/lib/types/user'

const updateClassSchema = z.object({
  name: z.string().min(1, '请输入班级名称').max(100),
  description: z.string().max(500).optional(),
})

type UpdateClassForm = z.infer<typeof updateClassSchema>

export function ClassDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: classInfo, isLoading } = useClassDetail(id!)
  const { data: members, isLoading: membersLoading } = useClassMembers(id!)
  const updateMutation = useUpdateClass()
  const addMemberMutation = useAddClassMember()
  const removeMemberMutation = useRemoveClassMember()

  const [submitting, setSubmitting] = useState(false)
  const [addMemberOpen, setAddMemberOpen] = useState(false)
  const [removeTarget, setRemoveTarget] = useState<{ userId: string; email: string } | null>(null)

  // 添加成员搜索状态
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedUser, setSelectedUser] = useState<UserPublic | null>(null)
  const [memberRole, setMemberRole] = useState('student')
  const debouncedQuery = useDebounce(searchQuery, 300)

  const { data: searchResults, isLoading: searching } = useUsers({
    q: debouncedQuery.length >= 2 ? debouncedQuery : undefined,
    size: 10,
  })

  // 已有成员 ID 集合
  const existingMemberIds = new Set(members?.items.map((m) => m.user_id) ?? [])

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<UpdateClassForm>({
    resolver: zodResolver(updateClassSchema),
    values: classInfo
      ? { name: classInfo.name, description: classInfo.description ?? '' }
      : undefined,
  })

  async function onUpdateSubmit(data: UpdateClassForm) {
    if (!id) return
    setSubmitting(true)
    updateMutation.mutate(
      { classId: id, data: { name: data.name, description: data.description || null } },
      {
        onSuccess: () => {
          toast.success('班级信息已更新')
          reset(data)
          setSubmitting(false)
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '更新失败')
          setSubmitting(false)
        },
      },
    )
  }

  function handleAddMember() {
    if (!id || !selectedUser) return
    addMemberMutation.mutate(
      { classId: id, data: { user_id: selectedUser.id, role: memberRole } },
      {
        onSuccess: () => {
          toast.success('成员已添加')
          setAddMemberOpen(false)
          setSearchQuery('')
          setSelectedUser(null)
          setMemberRole('student')
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '添加失败')
        },
      },
    )
  }

  function handleRemoveMember() {
    if (!id || !removeTarget) return
    removeMemberMutation.mutate(
      { classId: id, userId: removeTarget.userId },
      {
        onSuccess: () => {
          toast.success('成员已移除')
          setRemoveTarget(null)
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '移除失败')
        },
      },
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card className="max-w-2xl">
          <CardContent className="space-y-4 pt-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!classInfo) {
    return <div className="text-center text-muted-foreground py-12">班级不存在</div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="班级详情"
        description={classInfo.name}
        actions={
          <Button variant="outline" onClick={() => navigate('/admin/classes')}>
            返回列表
          </Button>
        }
      />

      {/* 班级信息编辑 */}
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>班级信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">名称</Label>
            <Input id="name" {...register('name')} />
            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">描述</Label>
            <Input id="description" {...register('description')} />
          </div>
          <Button
            type="button"
            disabled={submitting || !isDirty}
            onClick={() => handleSubmit(onUpdateSubmit)()}
          >
            {submitting ? '保存中...' : '保存'}
          </Button>
        </CardContent>
      </Card>

      {/* 成员列表 */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>班级成员</CardTitle>
          <Button size="sm" onClick={() => setAddMemberOpen(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            添加成员
          </Button>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>邮箱</TableHead>
                  <TableHead>姓名</TableHead>
                  <TableHead>角色</TableHead>
                  <TableHead>加入时间</TableHead>
                  <TableHead className="w-16">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {membersLoading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-40" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                      <TableCell><Skeleton className="h-5 w-12" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                      <TableCell><Skeleton className="h-8 w-8" /></TableCell>
                    </TableRow>
                  ))
                ) : members?.items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                      暂无成员
                    </TableCell>
                  </TableRow>
                ) : (
                  members?.items.map((member) => (
                    <TableRow key={member.user_id}>
                      <TableCell className="font-medium">{member.email}</TableCell>
                      <TableCell>{member.full_name ?? '-'}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{member.role}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(member.joined_at).toLocaleDateString('zh-CN')}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setRemoveTarget({ userId: member.user_id, email: member.email })}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* 添加成员弹窗 */}
      <Dialog
        open={addMemberOpen}
        onOpenChange={(open) => {
          setAddMemberOpen(open)
          if (!open) {
            setSearchQuery('')
            setSelectedUser(null)
            setMemberRole('student')
          }
        }}
      >
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>添加成员</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* 搜索输入 */}
            <div className="space-y-2">
              <Label>搜索用户</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="输入邮箱或姓名搜索..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value)
                    setSelectedUser(null)
                  }}
                  className="pl-9"
                />
              </div>
            </div>

            {/* 搜索结果列表 */}
            <div className="max-h-48 overflow-y-auto rounded-md border">
              {searching ? (
                <div className="space-y-2 p-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : debouncedQuery.length < 2 ? (
                <div className="p-4 text-center text-sm text-muted-foreground">
                  请输入至少 2 个字符搜索
                </div>
              ) : searchResults?.items.length === 0 ? (
                <div className="p-4 text-center text-sm text-muted-foreground">
                  未找到匹配的用户
                </div>
              ) : (
                searchResults?.items.map((user) => {
                  const isExisting = existingMemberIds.has(user.id)
                  const isSelected = selectedUser?.id === user.id
                  return (
                    <button
                      key={user.id}
                      type="button"
                      disabled={isExisting}
                      onClick={() => setSelectedUser(user)}
                      className={`flex w-full items-center gap-3 px-3 py-2 text-left text-sm transition-colors ${
                        isExisting
                          ? 'cursor-not-allowed opacity-50'
                          : isSelected
                            ? 'bg-primary/10'
                            : 'hover:bg-accent'
                      }`}
                    >
                      <div className="flex-1 min-w-0">
                        <p className="truncate font-medium">{user.email}</p>
                        <p className="truncate text-xs text-muted-foreground">
                          {user.full_name ?? '-'}
                        </p>
                      </div>
                      {isExisting ? (
                        <Badge variant="outline" className="shrink-0 text-xs">
                          已在班级中
                        </Badge>
                      ) : isSelected ? (
                        <Check className="h-4 w-4 shrink-0 text-primary" />
                      ) : null}
                    </button>
                  )
                })
              )}
            </div>

            {/* 已选用户 */}
            {selectedUser && (
              <div className="rounded-md border bg-muted/50 px-3 py-2 text-sm">
                已选择：<span className="font-medium">{selectedUser.email}</span>
                {selectedUser.full_name && (
                  <span className="text-muted-foreground">（{selectedUser.full_name}）</span>
                )}
              </div>
            )}

            {/* 角色选择 */}
            <div className="space-y-2">
              <Label>角色</Label>
              <Select value={memberRole} onValueChange={setMemberRole}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="teacher">教师</SelectItem>
                  <SelectItem value="student">学生</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddMemberOpen(false)}>
              取消
            </Button>
            <Button
              disabled={!selectedUser || addMemberMutation.isPending}
              onClick={handleAddMember}
            >
              {addMemberMutation.isPending ? '添加中...' : '添加'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 移除成员确认 */}
      <ConfirmDialog
        open={!!removeTarget}
        onOpenChange={(open) => !open && setRemoveTarget(null)}
        title="确认移除"
        description={`确定要将 ${removeTarget?.email ?? ''} 从班级中移除吗？`}
        confirmLabel="移除"
        variant="destructive"
        loading={removeMemberMutation.isPending}
        onConfirm={handleRemoveMember}
      />
    </div>
  )
}
