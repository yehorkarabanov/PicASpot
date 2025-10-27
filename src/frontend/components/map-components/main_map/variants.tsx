import { cva } from 'class-variance-authority'

export const mapVariants = cva('overflow-hidden', {
  variants: {
    variant: {
      default: 'bg-background',
      outline: 'border border-border/40 bg-background',
      ghost: 'bg-transparent',
    },
    rounded: {
      none: 'rounded-none',
      sm: 'rounded-sm',
      md: 'rounded-md',
      lg: 'rounded-lg',
      xl: 'rounded-xl',
    },
  },
  defaultVariants: {
    variant: 'default',
    rounded: 'lg',
  },
})
