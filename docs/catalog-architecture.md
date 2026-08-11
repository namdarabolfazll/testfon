# Catalog architecture

The `shop` app contains a production catalog model set for Dara Home.

## Models

- `Category`: hierarchical product categories with SEO fields and a processed category image.
- `Product`: catalog product content and merchandising flags. It does not store price or stock directly.
- `ProductImage`: gallery images. One image can be primary, and an image can optionally target a `ProductVariant`.
- `Attribute`: reusable product specification definition such as Material, Diameter, or Dishwasher Safe.
- `AttributeValue`: controlled choices for choice attributes.
- `CategoryAttribute`: allows each category to define relevant specifications.
- `ProductAttributeValue`: typed product specification values.
- `ProductOption`: sellable option dimension such as Color, Capacity, or Size.
- `ProductOptionValue`: available values for a product option.
- `ProductVariant`: sellable inventory unit with SKU, price, stock, and barcode.
- `VariantOptionValue`: selected option values for a variant.

## Product attributes vs variant options

Use `ProductAttributeValue` for specifications that describe the product and help filtering, such as material, diameter, or dishwasher safety.

Use `ProductOption` and `ProductOptionValue` only when the value creates a distinct sellable variant, such as Color = White or Capacity = 350ml.

## Product compatibility API

Templates can keep using:

- `product.name`
- `product.slug`
- `product.image`
- `product.price`
- `product.gallery`
- `category.image`

`product.image` returns the primary `ProductImage.image` file. `product.price` returns the lowest active variant price.

## Creating a product

1. Create a `Category`.
2. Create a `Product` with that category.
3. Create at least one `ProductVariant` with a unique SKU and price.
4. Create one or more `ProductImage` rows. Mark one as primary.

## Creating attributes

1. Create an `Attribute` with type `text`, `integer`, `decimal`, `boolean`, or `choice`.
2. For `choice` attributes, create `AttributeValue` rows.
3. Link the attribute to relevant categories with `CategoryAttribute`.
4. Assign typed values to products with `ProductAttributeValue`.

## Creating variants

1. Create product options such as Color and Capacity.
2. Create option values such as White and 350ml.
3. Create a `ProductVariant` with SKU, price, and stock.
4. Attach option values through `VariantOptionValue`.

Duplicate SKUs are prevented by a database constraint. Duplicate complete option combinations are validated at application level because SQL databases cannot portably enforce uniqueness across a variable number of related rows.

## Admin

The admin supports hierarchical category editing, product images and variants inline on products, searchable SKUs, attribute/value management, and category-specific attributes.
