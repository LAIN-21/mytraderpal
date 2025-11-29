import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Amplify } from 'aws-amplify'
import { config } from '@/lib/amplify-config'

const inter = Inter({ subsets: ['latin'] })

Amplify.configure(config)

export const metadata: Metadata = {
  title: 'MyTraderPal',
  description: 'Trading journal and strategy testing application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
