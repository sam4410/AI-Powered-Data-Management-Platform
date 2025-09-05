```markdown
# Metadata Catalog for Sales Table

## Table Overview
- **Table Name**: sales
- **Total Records**: 75,306
- **Overall Quality Score**: 0.638

## Validation Summary

| Column Name        | Completeness | Unique Values | Duplicates | Sample Values                       | Inferred Type  | Quality Score |
|--------------------|--------------|---------------|------------|-------------------------------------|----------------|----------------|
| sale_id            | 1.0          | 75,306        | 0          | 1, 2, 3, 4, 5                       | int64          | 1.0            |
| order_id           | 1.0          | 25,000        | 50,306     | 1, 2, 3, 4, 5                       | int64          | 0.666          |
| product_id         | 1.0          | 1,000         | 74,306     | 934, 997, 949, 321, 315             | int64          | 0.507          |
| quantity           | 1.0          | 10            | 75,296     | 1, 8, 2, 7, 10                      | int64          | 0.5            |
| unit_price         | 1.0          | 38,494        | 36,812     | 493.48, 412.54, 163.04, 105.65, 108.88 | float64       | 0.756          |
| total_price        | 1.0          | 63,220        | 12,086     | 493.48, 412.54, 1304.32, 211.3, 217.76 | float64       | 0.92           |
| discount_amount     | 1.0          | 31,950        | 43,356     | 35.9, 42.93, 50.26, 32.97, 29.41    | float64       | 0.712          |
| tax_amount          | 1.0          | 27,375        | 47,931     | 39.48, 33.0, 104.35, 16.9, 17.42     | float64       | 0.682          |
| sale_date          | 1.0          | 731           | 74,575     | 2024-09-02, 2024-02-20, 2025-05-26, 2024-05-25, 2023-09-28 | object       | 0.505          |
| salesperson_id     | 0.702        | 100           | 75,205     | 21.0, 31.0, 68.0, 72.0, 20.0        | float64       | 0.351          |
| commission         | 1.0          | 29,081        | 46,225     | 40.55, 41.54, 38.3, 12.58, 4.61     | float64       | 0.693          |
| profit_margin      | 1.0          | 31            | 75,275     | 0.13, 0.29, 0.23, 0.19, 0.26        | float64       | 0.5            |
| channel            | 1.0          | 5             | 75,301     | Phone, Website, Mobile App, Store, Marketplace | object       | 0.5            |

## Issues Found
- **Column**: salesperson_id
  - **Issue**: Low completeness
  - **Value**: 0.702
  - **Threshold**: 0.95

## Recommendations
- Review `salesperson_id`. Currently showing low completeness, consider providing default values or enforcing data entry rules to enhance data quality.
- Additional validation rules for other numeric columns to enforce valid ranges could also improve completeness and integrity.

## Conclusion
The "sales" table metadata has been successfully validated, revealing insights into data quality and completeness. Addressing the identified issues will greatly enhance data governance and usability.
```