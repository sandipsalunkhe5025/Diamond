import csv
import io

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


def get_price_from_sku(sku):
    sku_upper = sku.upper()
    if "-18K-" in sku_upper or sku_upper.endswith("-18K"):
        return 150
    elif "-14K-" in sku_upper or sku_upper.endswith("-14K"):
        return 100
    elif "-P-" in sku_upper or sku_upper.endswith("-P"):
        return 200
    return 0


def process_csv(input_file):

    content = input_file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")

    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Auto-detect delimiter (tab or comma)
    first_line = content.split('\n')[0]
    delimiter = '\t' if '\t' in first_line else ','

    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    raw_rows = list(reader)

    if not raw_rows:
        raise ValueError("The uploaded CSV file is empty.")

    # Strip whitespace from all keys and values
    input_rows = []
    for row in raw_rows:
        input_rows.append({k.strip(): (v.strip() if v else "") for k, v in row.items()})

    # Validate required columns
    required = {
        "Product sku",
        "data__product_name",
        "data__product_description",
        "data__diamond_can_be_matched_with",
    }
    available = set(input_rows[0].keys())
    missing = required - available
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    output_rows = []
    counter = 1

    for row in input_rows:
        product_sku  = row.get("Product sku", "")
        product_name = row.get("data__product_name", "")
        description  = row.get("data__product_description", "")
        stock        = row.get("data__qty", "")          # optional column
        price        = get_price_from_sku(product_sku)  # derived from SKU

        raw_shapes = row.get("data__diamond_can_be_matched_with", "")
        shapes = [s.strip() for s in raw_shapes.split(",") if s.strip()]

        if not shapes:
            continue

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

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(output_rows)

    return output.getvalue(), len(input_rows), len(output_rows)
def get_sample_combinations():
    metals = [
        "14KT Rose Gold", "14KT White Gold", "14KT Yellow Gold",
        "18KT Rose Gold", "18KT White Gold", "18KT Yellow Gold", "Platinum",
    ]
    shapes = [
        "Round", "Princess", "Cushion", "Radiant", "Asscher",
        "Emerald", "Oval", "Pear", "Marquise", "Heart",
    ]
    return [(metal, shape) for metal in metals for shape in shapes]
