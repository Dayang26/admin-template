import { BookOpen } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/lib/auth/context'

export function StudentHomePage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>欢迎回来，{user?.full_name ?? user?.email}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">这里是你的学习空间</p>

          {user?.class_memberships && user.class_memberships.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium">我的班级</h3>
              <div className="grid gap-2 sm:grid-cols-2">
                {user.class_memberships.map((cm) => (
                  <div
                    key={cm.class_id}
                    className="flex items-center gap-3 rounded-md border p-3"
                  >
                    <BookOpen className="h-5 w-5 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{cm.class_name}</p>
                    </div>
                    <Badge variant="secondary">{cm.role}</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
