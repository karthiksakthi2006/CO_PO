# Outcome-Based Education (OBE) Attainment Calculation Guide

## 1. Direct Attainment Calculation Methods

### Method A — Student Threshold Method (Standard OBE)
For every question $Q_k$ mapped to Course Outcome $CO_i$:

$$\text{eligible\_students} = \text{valid students under selected missing/absence policy}$$

$$\text{students\_meeting\_threshold} = \{s \in \text{eligible\_students} \mid \text{mark}(s, Q_k) \ge \text{threshold\_pct} \times \text{max\_marks}(Q_k)\}$$

$$\text{Attainment}(Q_k) = \left(\frac{|\text{students\_meeting\_threshold}|}{|\text{eligible\_students}|}\right) \times 100$$

### Method B — Normalized Score Method
$$\text{Attainment}(Q_k) = \left(\frac{\sum_{s} \text{mark}(s, Q_k)}{\sum_{s} \text{max\_marks}(Q_k)}\right) \times 100$$

## 2. CO Aggregation
For all questions $Q_1, \dots, Q_m$ mapped to $CO_i$ with weights $w_1, \dots, w_m$:

$$\text{Direct\_Attainment}(CO_i) = \frac{\sum_{k=1}^m \text{Attainment}(Q_k) \times w_k}{\sum_{k=1}^m w_k}$$

## 3. Direct & Indirect Attainment Combination
When Course Exit Surveys or Indirect Assessments are enabled:

$$\text{Overall\_Attainment}(CO_i) = \frac{\text{Direct} \times W_{\text{direct}} + \text{Indirect} \times W_{\text{indirect}}}{W_{\text{direct}} + W_{\text{indirect}}}$$

*Standard Configuration:* $W_{\text{direct}} = 80\%$, $W_{\text{indirect}} = 20\%$.

## 4. Gap Detection & Severity Classification
$$\text{gap\_percentage\_points} = \text{target\_attainment} - \text{actual\_attainment}$$

- **On Target**: $\text{gap} \le 0$ (Target met or exceeded)
- **Moderate Gap**: $0 < \text{gap} < 10$ percentage points below target
- **High Gap**: $10 \le \text{gap} < 20$ percentage points below target
- **Critical Gap**: $\text{gap} \ge 20$ percentage points below target

## 5. Program Outcome (PO/PSO) Attainment Matrix
For Program Outcome $PO_j$ and mapped outcomes $CO_i$ with mapping strength $S_{ij} \in \{0, 1, 2, 3\}$:

$$\text{Attainment}(PO_j) = \frac{\sum_{i} \text{Overall\_Attainment}(CO_i) \times S_{ij}}{\sum_{i} S_{ij}} \quad (\text{for } S_{ij} > 0)$$

$$\text{Average\_Strength}(PO_j) = \frac{\sum_{i} S_{ij}}{\text{Count}(S_{ij} > 0)}$$

## 6. Continuous Quality Improvement (CQI) Verification
$$\text{improvement\_percentage\_points} = \text{post\_intervention\_attainment} - \text{pre\_intervention\_attainment}$$
