# IEEE Research Report: TrustLens+
## Cognitive Load Reduction and LLM-Augmented Econometric Fraud Detection in E-Commerce

**Abstract** — The proliferation of manipulated reviews in e-commerce ecosystems fundamentally distorts algorithmic ranking and artificially inflates conversion rates, causing significant financial harm to consumers. We present **TrustLens+**, an interactive real-time market manipulation dashboard and IEEE-compliant analytical engine. TrustLens+ integrates Natural Language Processing (NLP), stylometric clustering, network graph theory, and econometric models to detect coordinated botnet activities and quantify their financial impact. Tested against a curated dataset of 50 high-value consumer electronics, our system demonstrates robust detection of rating distortions and provides an explainable AI (XAI) forensic audit trail for regulatory compliance.

---

### I. INTRODUCTION
Online review systems serve as the primary proxy for consumer trust. However, malicious actors frequently utilize botnets and click-farms to generate synthetic reviews, inflating a product’s perceived value. This manipulation leads to a direct "Consumer Overpay" effect, where buyers pay premium prices for substandard or average products. TrustLens+ addresses this challenge by moving beyond simple keyword filters toward a comprehensive, multi-modal forensic analysis system. 

### II. NOVEL METHODOLOGY & FEATURES
The TrustLens+ architecture relies on six fundamental analytical pillars (Features) to provide a holistic view of listing integrity.

#### A. Reviewer DNA Fingerprint (Stylometric Clustering)
Detecting automated text generation farms is challenging using traditional methods. TrustLens+ employs **TF-IDF (Term Frequency-Inverse Document Frequency)** to calculate lexical density and syntactic repetition. By plotting reviews in a multidimensional space (Semantic Alignment vs. Lexical Density), the system successfully isolates heavily clustered synthetic writing styles (bot behavior) from organic Gaussian variance.

#### B. Cross-Product Collusion Map
Manipulated accounts seldom target a single product. TrustLens+ implements a **Graph Theory Network Map** that explicitly isolated bot accounts operating across multiple product listings. Using network edges and nodes, the system draws linkages between the focus product and cross-collusion products (e.g., Headphones, Tablets), mapping out the orchestrated effort.

#### C. LLM Forensic Audit Trail
Black-box anomaly detection models fail to provide actionable regulatory intelligence. TrustLens+ incorporates an **Explainable AI (XAI)** module leveraging an LLM to generate a human-readable forensic audit trail. Based on the system's triggers, this module produces a narrative mapping flags to direct insights (e.g., "Discovered 60 accounts displaying perfectly isomorphic syntactic structures").

#### D. Sentiment-Star Mismatch Gauge
Review manipulators often generate 5-star ratings coupled with generic or scraped text that lacks genuine positive sentiment. TrustLens+ runs the review corpus through a **VADER (Valence Aware Dictionary and sEntiment Reasoner) NLP Sentiment Engine**. The application plots the explicitly provided Star Rating against the calculated VADER Polarity Score. A delta exceeding standard thresholds (e.g., > 0.4) strictly flags the listing for suspicious discrepancy.

#### E. Counterfactual True Price Engine
While detecting fake reviews is critical, quantifying the harm is equally important for policymakers. The platform utilizes a novel econometric impact model to compute the financial harm of manipulated reviews. By estimating a "Fair Market Value" (calculated by discounting the product's price proportional to the rating distortion), the system defines the explicit **Consumer Overpay**.

#### F. Market Manipulation Dashboard
To deliver top-down regulatory oversight, TrustLens+ aggregates individual product metrics into a **Total Simulated Illicit Revenue** dashboard. This visualizes ranked financial harm across the entire active monitor block of consumer electronics, emphasizing the macro-level damage caused by algorithmic inflation.

---

### III. IMPLEMENTATION OVERVIEW
The system is built as a high-fidelity, highly interactive demonstration:
1. **Frontend Architecture**: Implemented entirely in Python via **Streamlit** (v1) with a premium Aurora-themed glassmorphism CSS overlay, enabling a sophisticated "Premium" aesthetic without needing heavy frontend frameworks.
2. **Data Pipeline**: The system previously relied on noisy generic sets but was explicitly migrated to target **50 high-end consumer electronic devices** (e.g., GPUs, flagship smartphones, VR headsets). This ensures relevant, high-stakes financial calculations.
3. **Data Emulation & Caching**: Fallback data synthesis pipelines dynamically generate realistic footprint metrics (both organic and malicious templates) if backend databases (like Yelp/Amazon JSONs) are unreachable, ensuring 100% operational uptime for presentations. 
4. **Data Visualization**: Heavy reliance on `Plotly` graphs (scatter, gauge, networks, histograms) and `WordCloud` dynamically color-matched to the deep-space purple UI ensure visual impact.

### IV. ECONOMETRIC IMPACT RESULTS
Using a simulated distortion analysis on a ₹159,900 flagship smartphone with a +0.8 rating inflation:
* **True Value Projection:** Formulated downward adjustments reflect the removal of artificial purchase momentum.
* **Overpay Calculation:** Consumers are estimated to overpay significantly when trusting manipulated 4.9-star ratings over authentic 4.1-star metrics.
* **Monthly Revenue Simulation:** Scaling the overpay by simulated conversion volumes yields millions of rupees per product in artificially extracted consumer surplus.

### V. CONCLUSION
TrustLens+ represents a significant step forward from isolated sentiment analysis tools, offering an end-to-end econometric and forensic suite. By marrying NLP anomaly detection with graph-based collusion tracking and financial impact quantification, TrustLens+ provides a compelling framework for platforms, regulators, and consumers to restore trust in digital marketplaces.

---
**Prepared For:** IEEE Project Submission / Academic Demonstration
**System Status:** V1 (Streamlit App) FULLY ACTIVE & INTEGRATED. V2 (Vanilla HTML/JS) AVAILABLE FOR RAPID DEPLOYMENT.
