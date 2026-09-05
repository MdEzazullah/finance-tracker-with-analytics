# FinTrack — Personal Finance Tracker

A full-stack personal finance tracker built with **Python, Flask, and MySQL**, featuring secure authentication, budget tracking, and data analytics powered by **pandas** and **matplotlib**.

## Features

- **Secure Authentication** — signup/login with bcrypt password hashing, session-based access control
- **Transaction Management** — full CRUD for income and expense entries, filterable by category, type, and date
- **Budgeting** — set monthly limits per category, with live spent-vs-remaining tracking and over-budget alerts
- **Analytics Dashboard** — pandas-powered aggregation with three matplotlib visualizations:
  - Spending breakdown by category (pie chart)
  - Income vs. expense trend over the last 6 months (bar chart)
  - Budget vs. actual spending comparison (bar chart)
- **Custom UI** — each page (Login, Signup, Dashboard, Transactions, Budgets, Analytics) has its own distinct color theme and animations, built with hand-written CSS (no frameworks)
- **Profile Avatar** — Gravatar-based user avatar in the navigation bar

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL |
| Data Analysis | pandas |
| Visualization | matplotlib |
| Auth | bcrypt (password hashing) |
| Frontend | HTML, CSS (Jinja2 templating) |

## Project Structure