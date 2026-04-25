'use client'

import Image from 'next/image'
import { cn } from '@/lib/utils'

export interface Product {
  id: string
  name: string
  price: string | number
  image: string
  platform?: string
  link?: string
  reason?: string
  score?: number
  tags?: string[]
}

export interface ProductCardProps {
  product: Product
  compact?: boolean
}

export function ProductCard({ product, compact = false }: ProductCardProps) {
  const parsedPrice =
    typeof product.price === 'number'
      ? product.price
      : Number(String(product.price).replace(/[^0-9.]/g, ''))
  const displayPrice =
    Number.isFinite(parsedPrice) && parsedPrice > 0
      ? `₹${parsedPrice.toLocaleString()}`
      : String(product.price || 'Price N/A')

  const hasImage = Boolean(product.image)
  // Convert 0–1 score to 1–5 stars
  const stars = product.score ? Math.round(product.score * 5) : 0

  return (
    <div
      className={cn(
        'group rounded-xl border border-border overflow-hidden hover:border-primary hover:shadow-lg transition-all duration-200 bg-card',
        compact ? 'h-fit' : ''
      )}
    >
      {/* Image */}
      <div className={cn('relative overflow-hidden bg-muted', compact ? 'h-32' : 'h-44')}>
        {hasImage ? (
          <Image
            src={product.image}
            alt={product.name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            unoptimized
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-1 text-muted-foreground">
            <span className="text-3xl">📦</span>
            <span className="text-xs">No image</span>
          </div>
        )}
        {product.platform && (
          <div className="absolute top-2 left-2 bg-primary text-primary-foreground text-[10px] font-bold px-2 py-0.5 rounded-full">
            {product.platform}
          </div>
        )}
      </div>

      {/* Body */}
      <div className="p-3 space-y-2">
        <h3 className="font-semibold text-sm text-foreground line-clamp-2 leading-snug">
          {product.name}
        </h3>

        {/* Stars */}
        {stars > 0 && (
          <div className="flex gap-0.5">
            {[1, 2, 3, 4, 5].map((i) => (
              <span key={i} className={cn('text-xs', i <= stars ? 'text-amber-400' : 'text-muted')}>
                ★
              </span>
            ))}
          </div>
        )}

        {product.reason && (
          <p className="text-xs text-muted-foreground line-clamp-2">{product.reason}</p>
        )}

        {/* Tags */}
        {product.tags && product.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {product.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Price + View */}
        <div className="flex items-center justify-between pt-1">
          <span className="text-base font-bold text-primary">{displayPrice}</span>
          {product.link && (
            <a
              href={product.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1.5 rounded-lg bg-foreground text-background hover:bg-primary transition-colors font-semibold"
            >
              View
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
