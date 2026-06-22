import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Geist_Mono, Fraunces, Nunito } from 'next/font/google'
import { BookChatWidget } from '@/components/chat/book-chat-widget'
import './globals.css'

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

const fraunces = Fraunces({
  variable: '--font-fraunces',
  subsets: ['latin'],
  display: 'swap',
})

const nunito = Nunito({
  variable: '--font-nunito',
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Bookly — A Whimsical Little Bookstore',
  description:
    'Step into Bookly, a wholesome and magical bookstore where every page holds a little wonder. Discover hand-picked stories, cozy reads, and timeless treasures.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'light',
  themeColor: '#f3ecdc',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${nunito.variable} ${geistMono.variable} bg-background`}
    >
      <body className="font-sans antialiased">
        {children}
        <BookChatWidget />
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
