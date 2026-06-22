"use client"

import { useState } from "react"
import { Mail, Check } from "lucide-react"
import { Button } from "@/components/ui/button"

export function NewsletterSection() {
  const [submitted, setSubmitted] = useState(false)
  const [email, setEmail] = useState("")

  return (
    <section className="py-16 md:py-24">
      <div className="mx-auto max-w-4xl px-4 md:px-6">
        <div className="relative overflow-hidden rounded-[2rem] border border-accent/30 bg-accent/15 px-6 py-12 text-center md:px-12 md:py-16">
          <span className="mx-auto flex size-14 items-center justify-center rounded-full bg-accent text-accent-foreground">
            <Mail className="size-6" />
          </span>
          <h2 className="mt-5 font-serif text-3xl font-semibold tracking-tight text-foreground md:text-4xl text-balance">
            Letters from the shop
          </h2>
          <p className="mx-auto mt-3 max-w-md text-pretty leading-relaxed text-muted-foreground">
            Once a month, we send a little note with new arrivals, cozy reading
            lists, and the occasional secret discount. No spam, just stories.
          </p>

          {submitted ? (
            <p className="mx-auto mt-7 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 font-medium text-primary-foreground">
              <Check className="size-5" />
              You&apos;re on the list — welcome to the family!
            </p>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (email.trim()) setSubmitted(true)
              }}
              className="mx-auto mt-7 flex max-w-md flex-col gap-3 sm:flex-row"
            >
              <label htmlFor="newsletter-email" className="sr-only">
                Email address
              </label>
              <input
                id="newsletter-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="h-12 flex-1 rounded-full border border-border bg-card px-5 text-foreground outline-none transition-shadow placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/40"
              />
              <Button
                type="submit"
                size="lg"
                className="h-12 rounded-full bg-primary px-7 text-primary-foreground hover:bg-primary/90"
              >
                Subscribe
              </Button>
            </form>
          )}
        </div>
      </div>
    </section>
  )
}
