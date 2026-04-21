# Unordered Retrieved Context

This simulates a RAG-style retrieval result where the chunks are relevant but not
ordered by an authored investigation path.

## Retrieved Chunk A

Source: `Formats/shipmentRules.yaml`

`Shipment Check`

Inspect the shipment state after payment and inventory checks pass. Missing
shipment rows or delayed statuses suggest the problem has moved into fulfillment
or carrier handoff.

## Retrieved Chunk B

Source: `Formats/orderFulfillmentContext.yaml`

`Fulfillment Explanation Rules`

End by translating the route into an explanation that ties payment, inventory,
and shipment evidence back to the order state.

## Retrieved Chunk C

Source: `Formats/paymentRules.yaml`

`Payment Check`

Check the latest payment. A failed or declined payment blocks fulfillment
immediately.

## Retrieved Chunk D

Source: `Formats/postgresPatterns.yaml`

`SQL Latest Record Pattern`

Use a latest-record SQL pattern so the investigation works from the current
payment or shipment state rather than stale history.

## Retrieved Chunk E

Source: `Formats/inventoryRules.yaml`

`Inventory Availability Check`

Compare ordered quantities to available and reserved inventory to determine
whether stock is blocking shipment creation.

## Retrieved Chunk F

Source: `Formats/orderFulfillmentContext.yaml`

`Ecommerce Order Fulfillment`

Start from the authored overview of the fulfillment flow before moving into
specific checks.

All six chunks are relevant.

The problem is that retrieval alone does not say the intended route is:

1. overview
2. SQL pattern
3. payment
4. inventory
5. shipment
6. explanation
