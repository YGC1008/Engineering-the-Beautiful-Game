# Engineering the Beautiful Game

### A Data Engineering Analysis of Passing Patterns, Ball Progression, and Attacking Efficiency in the 2015–2016 English Premier League

## Project Overview

This project develops an end-to-end data engineering pipeline to analyze how passing patterns, progressive ball movement, and attacking sequences differ between winning, drawing, and losing teams in professional soccer matches.

Using StatsBomb Open Data from the 2015–2016 English Premier League, the project integrates Python, PostgreSQL, Apache Airflow, and Streamlit to transform raw event-level soccer data into structured analytical insights.

The project was developed as part of the WGU D610 Data Engineering Capstone.

## Research Question

**How do passing patterns, progressive ball movement, and attacking sequences differ between winning and losing teams in professional soccer matches?**

Drawn matches are included as an additional comparison group.

## Dataset

**Source:** [StatsBomb Open Data](https://github.com/hudl/open-data)

**Competition:** English Premier League  
**Season:** 2015–2016

| Dataset Component | Records |
|---|---:|
| Matches | 380 |
| Events | 1,313,773 |
| Team-match analytical records | 760 |

The event dataset includes passes, carries, shots, possessions, team identifiers, match identifiers, and event coordinates.

Raw and processed datasets are excluded from the repository because they can be regenerated using the provided extraction and transformation scripts.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data extraction, validation, transformation, and loading |
| PostgreSQL | Relational storage and analytical SQL |
| Apache Airflow | Pipeline orchestration and task dependencies |
| Pandas | Data processing and dashboard preparation |
| Streamlit | Interactive analytical dashboard |
| Plotly | Data visualization |
| Git and GitHub | Version control and project documentation |

## Data Engineering Architecture

The pipeline follows five sequential stages:

```text
StatsBomb Open Data
        |
        v
1. Extract JSON Data
        |
        v
2. Validate Data Quality
        |
        v
3. Transform into CSV
        |
        v
4. Load into PostgreSQL
        |
        v
5. Calculate Analytical Metrics
        |
        v
Streamlit Dashboard
```

Apache Airflow orchestrates the five processing tasks. The DAG is configured for manual execution, with task dependencies ensuring that each stage completes successfully before the next begins.

## Project Structure

```text
Engineering-the-Beautiful-Game/
├── dags/
│   └── capstone_pipeline.py
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── create_tables.sql
│   └── calculate_metrics.sql
├── src/
│   ├── extract.py
│   ├── validate.py
│   ├── transform.py
│   └── load.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Analytical Metrics

The PostgreSQL analytical layer calculates:

- Total and completed passes
- Pass completion rate
- Progressive passes and carries
- Final-third entries
- Total shots
- Expected goals (xG)
- Shot-producing possessions

For this project, progressive passes and carries are defined as successful movements advancing the ball by at least 10 coordinate units along the attacking direction. Final-third entries are identified when successful passes or carries cross the x-coordinate threshold of 80 on StatsBomb's 120-unit pitch.

These are project-specific operational definitions.

## Data Quality and Validation

The pipeline includes checks for JSON validity, duplicate event identifiers, required fields, and expected database row counts.

The loading process uses PostgreSQL transactions to roll back incomplete loads if an error occurs.

## Pipeline Execution

The Apache Airflow DAG is named `engineering_the_beautiful_game` and contains five tasks:

1. `extract`
2. `validate`
3. `transform`
4. `load`
5. `calculate_metrics`

The first successful manual execution completed all five tasks in approximately **3 minutes and 15 seconds**.

## Initial Analytical Findings

The analysis compares team-match performance across match outcomes.

| Metric | Win | Draw | Loss |
|---|---:|---:|---:|
| Average pass completion | 76.06% | 74.84% | 75.19% |
| Average progressive passes | 111.03 | 111.50 | 111.16 |
| Average progressive carries | 41.29 | 42.39 | 40.92 |
| Average shots | 14.15 | 13.45 | 11.60 |
| Average expected goals | 1.64 | 1.21 | 0.97 |
| Average final-third entries | 51.43 | 49.38 | 48.48 |

Winning teams generated more shots and higher expected goals on average, while progressive passing volumes were relatively similar across outcomes. These findings are descriptive associations rather than evidence that individual metrics cause victories.

## Interactive Dashboard

The Streamlit dashboard includes match-result and team filters, KPI summaries, metric comparisons, and a scatter plot examining pass completion against expected goals.

To launch the dashboard locally:

```bash
python -m streamlit run dashboard/app.py
```

The dashboard requires access to the populated PostgreSQL database.

## Reproducibility

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Create the PostgreSQL schema using `sql/create_tables.sql`, then run the extraction, validation, transformation, loading, and metric calculation scripts in sequence.

Configure the PostgreSQL connection and `PGPASSWORD` environment variable before executing database operations.

Apache Airflow must be installed separately with compatible Python and dependency versions. The DAG currently contains local project paths that should be adjusted when running on another computer.

## Limitations

- The analysis covers one Premier League season.
- The dataset reflects event-level actions rather than continuous player-tracking data.
- Progressive movement definitions are customized for this project.
- The pipeline requires a locally configured PostgreSQL database.
- The results identify associations and do not establish causality.

## Data Attribution

Event data is provided by StatsBomb through its publicly available open-data repository. Dataset usage remains subject to StatsBomb's attribution and licensing requirements.

**Source:** https://github.com/hudl/open-data