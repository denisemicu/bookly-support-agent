import { BookOpen, MapPin, Clock, Phone } from "lucide-react"

const columns = [
  {
    title: "Shop",
    links: ["New Arrivals", "Bestsellers", "Staff Picks", "Gift Cards", "Rare Finds"],
  },
  {
    title: "The Shop",
    links: ["Our Story", "Events & Readings", "Book Club", "Visit Us", "Careers"],
  },
  {
    title: "Help",
    links: ["Shipping", "Returns", "Track Order", "Contact Us", "FAQ"],
  },
]

export function SiteFooter() {
  return (
    <footer id="footer" className="scroll-mt-20 border-t border-border bg-secondary/40">
      <div className="mx-auto max-w-6xl px-4 py-14 md:px-6">
        <div className="grid gap-10 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <a href="#top" className="flex items-center gap-2.5">
              <span className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <BookOpen className="size-5" strokeWidth={2.25} />
              </span>
              <span className="font-serif text-2xl font-semibold text-primary">
                Bookly
              </span>
            </a>
            <p className="mt-4 max-w-xs text-pretty leading-relaxed text-muted-foreground">
              A wholesome little bookstore on the corner of Maple Lane, keeping
              the magic of reading alive one story at a time.
            </p>
            <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
              <li className="flex items-center gap-3">
                <MapPin className="size-4 shrink-0 text-primary" />
                14 Maple Lane, Old Town
              </li>
              <li className="flex items-center gap-3">
                <Clock className="size-4 shrink-0 text-primary" />
                Open daily, 9am till dusk
              </li>
              <li className="flex items-center gap-3">
                <Phone className="size-4 shrink-0 text-primary" />
                (555) 042-0199
              </li>
            </ul>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <h3 className="font-serif text-lg font-semibold text-foreground">
                {col.title}
              </h3>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-muted-foreground transition-colors hover:text-primary"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-border pt-6 text-sm text-muted-foreground sm:flex-row">
          <p>© {new Date().getFullYear()} Bookly. Made with tea and good stories.</p>
          <div className="flex gap-5">
            <a href="#" className="transition-colors hover:text-primary">
              Privacy
            </a>
            <a href="#" className="transition-colors hover:text-primary">
              Terms
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
