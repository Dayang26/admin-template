import { useRouteError, isRouteErrorResponse, Link } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export function RouteErrorPage() {
  const error = useRouteError()

  let title = '页面出错了'
  let message = '发生了未知错误'

  if (isRouteErrorResponse(error)) {
    if (error.status === 404) {
      title = '404'
      message = '抱歉，您访问的页面不存在'
    } else {
      title = String(error.status)
      message = error.statusText || '请求出错'
    }
  } else if (error instanceof Error) {
    message = error.message
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md text-center">
        <CardContent className="space-y-4 pt-8 pb-8">
          <AlertTriangle className="mx-auto h-16 w-16 text-destructive" />
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">{title}</h1>
            <p className="text-muted-foreground">{message}</p>
          </div>
          <div className="flex justify-center gap-2">
            <Button onClick={() => window.location.reload()}>刷新页面</Button>
            <Button variant="outline" asChild>
              <Link to="/">返回首页</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
