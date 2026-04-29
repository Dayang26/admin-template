import { Link } from 'react-router-dom'
import { FileQuestion } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@/lib/auth/context'
import { getDefaultRoute } from '@/lib/auth/routes'

export function NotFoundPage() {
  const { user } = useAuth()

  const homeUrl = user ? getDefaultRoute(user) : '/login'

  const homeLabel = user ? '返回首页' : '去登录'

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md text-center">
        <CardContent className="space-y-4 pt-8 pb-8">
          <FileQuestion className="mx-auto h-16 w-16 text-muted-foreground" />
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">404</h1>
            <p className="text-muted-foreground">抱歉，您访问的页面不存在</p>
          </div>
          <Button asChild>
            <Link to={homeUrl}>{homeLabel}</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
