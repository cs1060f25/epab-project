import './globals.css'

export const metadata = {
  title: 'CS12-1 Prototype 4: Jupyter Interactive Investigation',
  description: 'Incident Timeline & Evidence Assembly - Data Science Notebook Environment',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}