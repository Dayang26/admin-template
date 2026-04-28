import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getClasses,
  getClassDetail,
  createClass,
  updateClass,
  deleteClass,
  getClassMembers,
  addClassMember,
  removeClassMember,
  type ClassSearchParams,
  type ClassCreateData,
  type ClassUpdateData,
  type ClassMemberAddData,
} from '../api/classes'

export function useClasses(params: ClassSearchParams = {}) {
  return useQuery({
    queryKey: ['classes', params],
    queryFn: () => getClasses(params),
  })
}

export function useClassDetail(classId: string) {
  return useQuery({
    queryKey: ['classes', classId],
    queryFn: () => getClassDetail(classId),
    enabled: !!classId,
  })
}

export function useCreateClass() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: ClassCreateData) => createClass(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] })
    },
  })
}

export function useUpdateClass() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ classId, data }: { classId: string; data: ClassUpdateData }) =>
      updateClass(classId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] })
    },
  })
}

export function useDeleteClass() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (classId: string) => deleteClass(classId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] })
    },
  })
}

export function useClassMembers(classId: string, params: { page?: number; size?: number } = {}) {
  return useQuery({
    queryKey: ['classes', classId, 'members', params],
    queryFn: () => getClassMembers(classId, params),
    enabled: !!classId,
  })
}

export function useAddClassMember() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ classId, data }: { classId: string; data: ClassMemberAddData }) =>
      addClassMember(classId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['classes', variables.classId, 'members'] })
    },
  })
}

export function useRemoveClassMember() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ classId, userId }: { classId: string; userId: string }) =>
      removeClassMember(classId, userId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['classes', variables.classId, 'members'] })
    },
  })
}
