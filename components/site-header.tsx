"use client"

import { useState } from "react"
import { BookOpen, Search, ShoppingBag, Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"

const navLinks = [
  { label: "New Arrivals", href: "#featured" },
  { label: "Browse Shelves", href: "#categories" },
  { label: "Our Story", href: "#story" },
  { label: "Visit Us", href: "#footer" },
]

export function SiteHeader() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 md:px-6">
        <a href="#top" className="flex items-center gap-2.5">
          <span className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <BookOpen className="size-5" strokeWidth={2.25} />
          </span>
          <span className="font-serif text-2xl font-semibold tracking-tight text-primary">
            Bookly
          </span>
        </a>

        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm font-medium text-foreground/80 transition-colors hover:text-primary"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-1.5">
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full text-foreground/80 hover:bg-secondary hover:text-primary"
            aria-label="Search the shelves"
          >
            <Search className="size-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="relative rounded-full text-foreground/80 hover:bg-secondary hover:text-primary"
            aria-label="View your basket"
          >
            <ShoppingBag className="size-5" />
            <span className="absolute -right-0.5 -top-0.5 flex size-4 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-accent-foreground">
              3
            </span>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full text-foreground/80 md:hidden"
            aria-label="Toggle menu"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </Button>
        </div>
      </div>

      {open && (
        <nav
          className="border-t border-border/60 bg-background px-4 py-3 md:hidden"
          aria-label="Mobile"
        >
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block rounded-lg px-3 py-2.5 text-sm font-medium text-foreground/80 hover:bg-secondary hover:text-primary"
            >
              {link.label}
            </a>
          ))}
        </nav>
      )}
    </header>
  )
}
