import './globals.css'

export const metadata = {
  title: 'Security Alert Dashboard',
  description: 'Unified AI-Driven Cybersecurity & Fraud Detection',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
