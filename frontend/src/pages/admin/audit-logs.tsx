import { useState } from 'react'
import { Search, RefreshCw } from 'lucide-react'
import { Input } from '@/components/ui/input'
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PageHeader } from '@/components/shared/page-header'
import { useAuditLogs } from '@/lib/hooks/use-audit-logs'

const ACTION_OPTIONS = [
  '用户登录',
  '更新个人资料',
  '修改密码',
  '创建用户',
  '更新用户',
  '删除用户',
  '创建角色',
  '更新角色',
  '删除角色',
  '更新角色权限',
]

const METHOD_COLORS: Record<string, string> = {
  POST: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  PATCH: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  PUT: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  DELETE: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}

export function AuditLogsPage() {
  const [page, setPage] = useState(1)
  const [emailSearch, setEmailSearch] = useState('')
  const [actionFilter, setActionFilter] = useState('')

  const { data, isLoading, refetch, isFetching } = useAuditLogs({
    page,
    size: 20,
    user_email: emailSearch || undefined,
    action: actionFilter || undefined,
  })

  return (
    <div className="space-y-6">
      <PageHeader
        title="操作日志"
        description="查看系统操作记录"
        actions={
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
            刷新
          </Button>
        }
      />

      {/* 筛选 */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索用户邮箱..."
            value={emailSearch}
            onChange={(e) => {
              setEmailSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
          />
        </div>
        <Select
          value={actionFilter}
          onValueChange={(v) => {
            setActionFilter(v === 'all' ? '' : v)
            setPage(1)
          }}
        >
          <SelectTrigger className="w-44">
            <SelectValue placeholder="操作类型" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部操作</SelectItem>
            {ACTION_OPTIONS.map((action) => (
              <SelectItem key={action} value={action}>
                {action}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 表格 */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-44">时间</TableHead>
              <TableHead>用户</TableHead>
              <TableHead className="w-20">方法</TableHead>
              <TableHead>操作</TableHead>
              <TableHead>详情</TableHead>
              <TableHead className="w-32">IP</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-36" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-14" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                  暂无日志记录
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="text-muted-foreground text-xs">
                    {new Date(log.created_at).toLocaleString('zh-CN')}
                  </TableCell>
                  <TableCell className="font-medium text-sm">{log.user_email}</TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium ${METHOD_COLORS[log.method] ?? ''}`}
                    >
                      {log.method}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{log.action}</Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground max-w-xs truncate" title={log.detail ?? ''}>
                    {log.detail ?? '-'}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">{log.ip_address ?? '-'}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* 分页 */}
      {data && (
        <div className={`flex items-center ${data.pages > 1 ? 'justify-between' : 'justify-center'}`}>
          <p className="text-sm text-muted-foreground">
            共 {data.total} 条{data.pages > 1 && `，第 ${page}/${data.pages} 页`}
          </p>
          {data.pages > 1 && (
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                上一页
              </Button>
              <Button variant="outline" size="sm" disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)}>
                下一页
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
