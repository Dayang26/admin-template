export function getUserInitials(fullName: string | null | undefined, email: string): string {
  if (fullName) {
    return fullName
      .split(' ')
      .map((name) => name[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return email[0]?.toUpperCase() ?? '?'
}
