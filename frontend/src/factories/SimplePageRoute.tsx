import * as React from 'react'
import {
  createFileRoute,
  type ErrorComponentProps,
} from '@tanstack/react-router'
import { NotFound } from '~/components/NotFound'

function DefaultErrorComponent({ error }: ErrorComponentProps) {
  return (
    <div className="text-red-600 p-4">
      <strong>Error:</strong> {error.message}
    </div>
  )
}

type SimpleRouteOptions = {
  component: () => JSX.Element
  loader?: (opts: any) => Promise<any>
  errorComponent?: (props: ErrorComponentProps) => JSX.Element
}

export function simplePageRoute<TPath extends string>(
  path: TPath,
  {
    component,
    loader,
    errorComponent = DefaultErrorComponent,
  }: SimpleRouteOptions
) {
  return createFileRoute(path as any)({
    component,
    loader,
    errorComponent,
  })
}
