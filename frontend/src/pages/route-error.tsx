import { useRouteError, isRouteErrorResponse, Link } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ApiError } from '@/lib/api/client'

function getRouteErrorCopy(status: number, fallback = '请求出错') {
  if (status === 401) {
    return { title: '401', message: '登录状态已过期，请重新登录' }
  }

  if (status === 403) {
    return { title: '403', message: '权限不足，无法访问该页面' }
  }

  if (status === 404) {
    return { title: '404', message: '抱歉，您访问的页面不存在' }
  }

  if (status >= 500) {
    return { title: String(status), message: '服务器暂时不可用，请稍后重试' }
  }

  return { title: String(status), message: fallback }
}

export function RouteErrorPage() {
  const error = useRouteError()

  let title = '页面出错了'
  let message = '发生了未知错误'

  if (isRouteErrorResponse(error)) {
    const copy = getRouteErrorCopy(error.status, error.statusText || '请求出错')
    title = copy.title
    message = copy.message
  } else if (error instanceof ApiError) {
    const copy = getRouteErrorCopy(error.status, error.message)
    title = copy.title
    message = copy.message
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
