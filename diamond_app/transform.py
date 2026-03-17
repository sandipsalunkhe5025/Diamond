import csv
import io

# Output CSV column order — matches WooCommerce variation import format
OUTPUT_FIELDS = [
    "ID",
    "Type",
    "SKU",
    "Name",
    "Published",
    "Is featured?",
    "Visibility in catalog",
    "Short description",
    "Description",
    "Stock",
    "Price",
]


def process_csv(input_file):
    """
    Transform the input product CSV into WooCommerce variation rows.

    Logic:
      - Each input row has one metal (data__metal_name) and multiple shapes
        (data__diamond_can_be_matched_with, comma-separated in one cell).
      - For every input row, one output row is created per shape.
      - Output SKU  = <Product sku>-<Shape>    e.g. SL0001-14K-R-Round
      - Output Name = <data__product_name> with <Shape>
      - Description = data__product_description
      - Stock / Price carried over from the input row.
    """
    content = input_file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")  # strip BOM if present

    reader = csv.DictReader(io.StringIO(content))
    input_rows = list(reader)

    if not input_rows:
        raise ValueError("The uploaded CSV file is empty.")

    # Validate required columns exist
    required = {
        "Product sku",
        "data__product_name",
        "data__product_description",
        "data__diamond_can_be_matched_with",
        "Price",
        "data__qty",
    }
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    output_rows = []
    counter = 1

    for row in input_rows:
        product_sku  = row.get("Product sku", "").strip()
        product_name = row.get("data__product_name", "").strip()
        description  = row.get("data__product_description", "").strip()
        price        = row.get("Price", "").strip()
        stock        = row.get("data__qty", "").strip()

        # Shapes are comma-separated in one cell — split them out
        raw_shapes = row.get("data__diamond_can_be_matched_with", "")
        shapes = [s.strip() for s in raw_shapes.split(",") if s.strip()]

        for shape in shapes:
            output_rows.append({
                "ID":                    counter,
                "Type":                  "variation",
                "SKU":                   f"{product_sku}-{shape}",
                "Name":                  f"{product_name} with {shape}",
                "Published":             1,
                "Is featured?":          0,
                "Visibility in catalog": "visible",
                "Short description":     "",
                "Description":           description,
                "Stock":                 stock,
                "Price":                 price,
            })
            counter += 1

    # Write output CSV to string
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(output_rows)

    return output.getvalue(), len(input_rows), len(output_rows)


def get_sample_combinations():
    """Return all 70 (metal, shape) pairs for dashboard preview."""
    metals = [
        "14KT Rose Gold", "14KT White Gold", "14KT Yellow Gold",
        "18KT Rose Gold", "18KT White Gold", "18KT Yellow Gold", "Platinum",
    ]
    shapes = [
        "Round", "Princess", "Cushion", "Radiant", "Asscher",
        "Emerald", "Oval", "Pear", "Marquise", "Heart",
    ]
    return [(metal, shape) for metal in metals for shape in shapes]