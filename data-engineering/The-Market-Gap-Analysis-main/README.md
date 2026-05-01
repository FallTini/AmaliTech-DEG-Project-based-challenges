# Sugar Trap Analysis - Open Food Facts Project

---

## A. Executive Summary

This project analyzes ~499,684 food products from the Open Food Facts dataset to identify high-protein, low-sugar market opportunities. Using data cleaning, category classification, and exploratory analysis, we uncovered clear “Blue Ocean” segments where consumer demand for healthier products is not yet fully met.  

The analysis reveals that Dairy, Condiments, and Cereals represent the strongest opportunity areas, with Dairy showing the highest proportion of protein-rich and low-sugar products. A Streamlit dashboard was built to visualize nutrient patterns, category-level opportunity rates, and ingredient insights to support data-driven product strategy decisions for CPG companies.

---

## B. Project Links

- **Link to Notebook:** https://colab.research.google.com/drive/1rsfd81DzzqhbdekgYG0D6P22qJFjF1dC?usp=sharing

- **Link to Dashboard:** https://m5qtcryfxxj6sciiyoykul.streamlit.app/

- **Link to Presentation:** https://docs.google.com/presentation/d/1pWLlRLt0Y1VhbIJwbdo1yc1VEAQ1HLOm/edit?usp=sharing&ouid=117936114877771029434&rtpof=true&sd=true
  - Slide Deck (PDF/PPT): 

---

## C. Technical Explanation

### Data Cleaning Approach
The dataset was cleaned by:
- Removing biologically invalid values (e.g., sugars/proteins outside 0–100g range)
- Handling missing values in key nutrient columns
- Standardizing category tags by removing language prefixes (e.g., en:, fr:, de:)
- Reducing noise in ingredient data for downstream analysis

Due to the high percentage of missing category tags (~61%), a two-pass classification system was implemented:
1. Keyword-based assignment using nutritional and product-based heuristics
2. Secondary classification using product name inference for unclassified items

This improved category coverage significantly while maintaining data integrity.

---

### Candidate’s Choice (Bonus Analysis)
A custom “Market Size vs Opportunity Rate” bubble chart was introduced to enhance decision-making. Unlike simple opportunity rate analysis, this visualization combines:
- Category size (number of products)
- Opportunity rate (high-protein, low-sugar percentage)

This allows stakeholders to prioritize categories that are both large in market size and high in innovation potential, making it more actionable for product strategy decisions.

---







