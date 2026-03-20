import React from "react";
import type { AddonContext } from "@wealthfolio/addon-sdk";
import { Button, Card, CardContent, Icons } from "@wealthfolio/ui";

function AddonExample({ ctx }: { ctx: AddonContext }) {
  const handleSync = () => {
    ctx.api.logger.info("Sync button clicked");
  };

  return (
    <div className="p-6">
      <Card>
        <CardContent className="p-6">
          <h1 className="text-2xl font-semibold mb-2">
            wealthfolio-actualbudget-sync
          </h1>
          <p className="text-muted-foreground">
            Welcome to your new Wealthfolio addon! Start building amazing
            features.
          </p>
          <Button className="mt-4" onClick={handleSync}>
            Sync
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default function enable(ctx: AddonContext) {
  // Add a sidebar item
  const sidebarItem = ctx.sidebar.addItem({
    id: "wealthfolio-actualbudget-sync",
    label: "wealthfolio-actualbudget-sync",
    icon: <Icons.Blocks className="h-5 w-5" />,
    route: "/addon/wealthfolio-actualbudget-sync",
    order: 100,
  });

  // Add a route
  const Wrapper = () => <AddonExample ctx={ctx} />;
  ctx.router.add({
    path: "/addon/wealthfolio-actualbudget-sync",
    component: React.lazy(() => Promise.resolve({ default: Wrapper })),
  });

  // Cleanup on disable
  ctx.onDisable(() => {
    try {
      sidebarItem.remove();
    } catch (err) {
      ctx.api.logger.error("Failed to remove sidebar item:", err);
    }
  });
}
