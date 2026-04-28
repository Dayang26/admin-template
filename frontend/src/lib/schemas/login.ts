import { z } from 'zod'

export const loginFormSchema = z.object({
  email: z
    .string()
    .min(1, { message: '请输入邮箱' })
    .email({ message: '请输入有效的邮箱地址' }),
  password: z
    .string()
    .min(1, { message: '请输入密码' })
    .min(6, { message: '密码至少为 6 位' }),
})

export type LoginFormValues = z.infer<typeof loginFormSchema>
