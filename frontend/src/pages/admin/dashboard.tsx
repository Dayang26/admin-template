import { Users, UserCheck, PieChart, ShieldCheck } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/shared/page-header'
import { useDashboardStats } from '@/lib/hooks/use-dashboard'
import ReactCountUp from 'react-countup'

const CountUp = (ReactCountUp as unknown as { default: typeof ReactCountUp }).default ?? ReactCountUp

const ROLE_LABELS: Record<string, string> = {
  superuser: '超级管理员',
}

export function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats()

  return (
    <div className="space-y-6">
      <PageHeader title="仪表盘" description="系统概览" />

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">用户总数</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                <CountUp end={stats?.total_users ?? 0} duration={2} />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">活跃用户</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                <CountUp end={stats?.active_users ?? 0} duration={2} />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">权限模型</CardTitle>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">RBAC</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">角色分布</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-32" />
            ) : stats?.role_distribution ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(stats.role_distribution).map(([role, count]) => (
                  <Badge key={role} variant="secondary">
                    {ROLE_LABELS[role] ?? role}: {count}
                  </Badge>
                ))}
              </div>
            ) : (
              <span className="text-sm text-muted-foreground">暂无数据</span>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
