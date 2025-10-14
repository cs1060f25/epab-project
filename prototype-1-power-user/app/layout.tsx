import './globals.css'

export const metadata = {
  title: 'CS12-1 Prototype 1: Power User Dashboard',
  description: 'Incident Timeline & Evidence Assembly with Natural Language Assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-dark-bg text-white">{children}</body>
    </html>
  )
}