import {
  Wand2,
  Compass,
  Heart,
  Leaf,
  Moon,
  Coffee,
  type LucideIcon,
} from "lucide-react"

type Category = {
  name: string
  blurb: string
  count: string
  icon: LucideIcon
}

const categories: Category[] = [
  {
    name: "Fairytales & Folklore",
    blurb: "Old magic, retold by the fireside.",
    count: "320 books",
    icon: Wand2,
  },
  {
    name: "Wander & Wonder",
    blurb: "Maps, voyages and faraway places.",
    count: "210 books",
    icon: Compass,
  },
  {
    name: "Hopeful Romance",
    blurb: "Slow burns and happy little endings.",
    count: "415 books",
    icon: Heart,
  },
  {
    name: "Garden & Hearth",
    blurb: "Cozy living, plants and slow days.",
    count: "180 books",
    icon: Leaf,
  },
  {
    name: "Midnight Mysteries",
    blurb: "Puzzles to unravel under lamplight.",
    count: "265 books",
    icon: Moon,
  },
  {
    name: "Comfort Classics",
    blurb: "The well-loved stories worth rereading.",
    count: "390 books",
    icon: Coffee,
  },
]

export function CategoriesSection() {
  return (
    <section id="categories" className="scroll-mt-20 py-16 md:py-24">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="mx-auto max-w-2xl text-center text-balance">
          <p className="font-serif text-lg italic text-accent-foreground">
            Find your nook
          </p>
          <h2 className="font-serif text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
            Wander through our little shelves
          </h2>
          <p className="mt-4 text-pretty text-muted-foreground">
            Every corner of Bookly has its own character. Follow your mood and
            see where the stories take you.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat) => {
            const Icon = cat.icon
            return (
              <a
                key={cat.name}
                href="#featured"
                className="group flex items-start gap-4 rounded-2xl border border-border bg-card p-6 transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10"
              >
                <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <Icon className="size-6" strokeWidth={2} />
                </span>
                <div>
                  <h3 className="font-serif text-xl font-semibold text-foreground">
                    {cat.name}
                  </h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                    {cat.blurb}
                  </p>
                  <span className="mt-2 inline-block text-xs font-semibold uppercase tracking-wide text-accent-foreground">
                    {cat.count}
                  </span>
                </div>
              </a>
            )
          })}
        </div>
      </div>
    </section>
  )
}
