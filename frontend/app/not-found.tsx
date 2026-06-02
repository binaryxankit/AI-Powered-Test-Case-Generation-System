import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="container flex flex-col items-center justify-center py-24 text-center">
      <p className="text-sm font-medium uppercase tracking-wider text-primary">
        404
      </p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight">
        Page not found
      </h1>
      <p className="mt-2 max-w-sm text-muted-foreground">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Button asChild className="mt-6">
        <Link href="/">Back home</Link>
      </Button>
    </div>
  );
}
