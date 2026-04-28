import { useQuery } from '@tanstack/react-query'
import { getMyClasses, getMyClassMembers } from '../api/teacher'

export function useMyClasses() {
  return useQuery({
    queryKey: ['teacher', 'classes'],
    queryFn: getMyClasses,
  })
}

export function useMyClassMembers(classId: string, params: { page?: number; size?: number } = {}) {
  return useQuery({
    queryKey: ['teacher', 'classes', classId, 'members', params],
    queryFn: () => getMyClassMembers(classId, params),
    enabled: !!classId,
  })
}
