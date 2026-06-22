import Image from "next/image"
import { Star } from "lucide-react"
import { Button } from "@/components/ui/button"

const books = [
  {
    title: "The Lantern Keeper",
    author: "Eloise Marsh",
    price: "$18",
    rating: "4.9",
    tag: "Staff Pick",
    image: "/images/book-1.png",
  },
  {
    title: "Moonlit Cartography",
    author: "Idris Vale",
    price: "$22",
    rating: "4.8",
    tag: "New",
    image: "/images/book-2.png",
  },
  {
    title: "The Tea Garden Letters",
    author: "Posy Ainsworth",
    price: "$16",
    rating: "5.0",
    tag: "Beloved",
    image: "/images/book-3.png",
  },
  {
    title: "Whispers of the Willow",
    author: "Cormac Birch",
    price: "$20",
    rating: "4.7",
    tag: "Cozy Read",
    image: "/images/book-4.png",
  },
]

export function FeaturedBooks() {
  return (
    <section id="featured" className="scroll-mt-20 bg-secondary/40 py-16 md:py-24">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="flex flex-col items-end justify-between gap-4 sm:flex-row">
          <div className="text-balance">
            <p className="font-serif text-lg italic text-accent-foreground">
              Fresh off the cart
            </p>
            <h2 className="font-serif text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
              This week&apos;s little treasures
            </h2>
          </div>
          <Button
            variant="link"
            className="px-0 text-base text-primary"
            nativeButton={false}
            render={<a href="#categories" />}
          >
            See the whole shelf
          </Button>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {books.map((book) => (
            <article
              key={book.title}
              className="group flex flex-col overflow-hidden rounded-2xl border border-border bg-card p-3 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-primary/10"
            >
              <div className="relative overflow-hidden rounded-xl bg-secondary/60">
                <span className="absolute left-3 top-3 z-10 rounded-full bg-accent px-2.5 py-1 text-xs font-bold text-accent-foreground">
                  {book.tag}
                </span>
                <Image
                  src={book.image || "/placeholder.svg"}
                  alt={`Cover of ${book.title} by ${book.author}`}
                  width={300}
                  height={400}
                  className="h-60 w-full object-contain p-4 transition-transform duration-300 group-hover:scale-105"
                />
              </div>
              <div className="flex flex-1 flex-col gap-1 px-2 pb-2 pt-4">
                <div className="flex items-center gap-1 text-accent-foreground">
                  <Star className="size-3.5 fill-current" />
                  <span className="text-xs font-semibold text-foreground">
                    {book.rating}
                  </span>
                </div>
                <h3 className="font-serif text-lg font-semibold leading-snug text-foreground">
                  {book.title}
                </h3>
                <p className="text-sm text-muted-foreground">{book.author}</p>
                <div className="mt-auto flex items-center justify-between pt-3">
                  <span className="font-serif text-xl font-semibold text-primary">
                    {book.price}
                  </span>
                  <Button
                    size="sm"
                    className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    Add to basket
                  </Button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
