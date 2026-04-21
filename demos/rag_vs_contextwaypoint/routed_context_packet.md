# Routed Context Packet

This is the same problem rendered as an authored route.

## Step 1 - Ecommerce Order Fulfillment

Source: `Formats/orderFulfillmentContext.yaml`
Path: `Ecommerce Order Fulfillment`
Weight: `100`

Start with the authored overview of the fulfillment flow. This domain context
defines the order states, the relationship between payment, inventory, and
shipment, and the expectation that the investigation should move from broad
status to specific checks before returning to a final explanation.

## Step 2 - SQL Latest Record Pattern

Source: `Formats/postgresPatterns.yaml`
Path: `Postgres Troubleshooting Patterns > SQL Latest Record Pattern`
Weight: `95`

When the route asks for the most recent payment or shipment event, start with a
latest-record query pattern. Pull the newest status row per order so downstream
checks work from the current state rather than stale history.

## Step 3 - Payment Check

Source: `Formats/paymentRules.yaml`
Path: `Payment Rules > Payment Check`
Weight: `95`

Check the latest payment for the order. A failed or declined payment stops
fulfillment immediately, while an authorized or captured payment keeps the route
moving toward inventory and shipment checks.

## Step 4 - Inventory Availability Check

Source: `Formats/inventoryRules.yaml`
Path: `Inventory Rules > Inventory Availability Check`
Weight: `90`

Compare ordered quantities against available and reserved inventory. A paid
order without enough stock should remain blocked before shipment creation, even
when the payment path itself looks healthy.

## Step 5 - Shipment Check

Source: `Formats/shipmentRules.yaml`
Path: `Shipment Rules > Shipment Check`
Weight: `88`

Inspect the shipment state only after payment and inventory checks pass. Missing
shipment rows, stale labels, or delayed shipment statuses indicate that the
issue has moved into the fulfillment or carrier handoff stage.

## Step 6 - Fulfillment Explanation Rules

Source: `Formats/orderFulfillmentContext.yaml`
Path: `Ecommerce Order Fulfillment > Fulfillment Explanation Rules`
Weight: `55`

End by translating the route into an explanation. The final answer should tie
the observed payment, inventory, and shipment evidence back to the order state
and explain which dependency blocked fulfillment.
