export function formatPageTitle(pageName: string, template: string, systemName: string): string {
  if (!template) {
    return `${pageName} - ${systemName}`
  }
  
  return template
    .replace('{page}', pageName)
    .replace('{systemName}', systemName)
}
