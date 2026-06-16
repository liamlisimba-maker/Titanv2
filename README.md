# TITAN v4.0 — AI-Assisted Crypto Trading System

**TITAN** is a high-performance, multi-user, Telegram-first cryptocurrency trading system engineered for capital preservation, rigorous risk management, and consistent growth. Built on a modular architecture, TITAN ensures scalability and resilience across multiple trading waves.

---

## 🛡️ The TITAN Laws
1. **Survival > Profit**: Capital preservation is the absolute priority.
2. **Risk Engine > Strategy**: No strategy executes without strict risk validation.
3. **Exchange Truth > Local State**: Always verify positions against the exchange.
4. **No Position Without Stop Loss**: Every trade must have a defined exit.
5. **Logs > Assumptions**: Every action is audited; nothing is assumed.
6. **Consistency > Home Runs**: Sustainable growth over high-risk gambles.
7. **Paper First. Live Later**: 21 days + 100 trades of paper trading required before live execution.

---

## 🏗️ Project Structure (Wave 1 — Foundation)

The current phase establishes the core foundation of the system:

- **`bot/`**: Telegram interface, command routing, and standardized response templates.
- **`core/`**: Critical logic for user management, audit trails, and system health monitoring.
- **`db/`**: Async SQLite data layer with WAL mode for high concurrency and safety.
- **`tools/`**: Abstraction layer for external integrations (Binance, News, TradingView).
- **`config/`**: Centralized management of system constants and environment settings.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Telegram Bot Token (via [@BotFather](https://t.me/botfather))

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/liamlisimba-maker/Titanv2.git
   cd Titanv2
   ```

2. **Environment Setup**:
   Copy the example environment file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

3. **Generate Admin Security**:
   Run the utility to generate your secure admin PIN hash:
   ```bash
   python scripts/generate_pin_hash.py
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Launch TITAN**:
   ```bash
   python main.py
   ```

---

## 📅 Roadmap

### Wave 1: Foundation (Current)
- [x] Modular Repository Scaffolding
- [x] Async SQLite Data Layer & Migrations
- [x] Role-Based User Management (Pending/Active/Suspended)
- [x] Immutable Audit Trail System
- [x] System Health & Resource Monitoring

### Wave 2: Intelligence (Pending)
- [ ] Signal Ingestion & Scoring Engine
- [ ] Alpha TrendFlow Strategy Implementation
- [ ] Sentiment & News Analysis Integration

### Wave 3: Execution (Pending)
- [ ] Binance API Integration
- [ ] Risk Management & Order Execution Engine
- [ ] Paper Trading & Live Trading Activation

---

## 🔒 Security
TITAN implements a session-based PIN authorization for all administrative actions and an immutable audit log to ensure every sensitive operation is recorded and verifiable.

---
*Disclaimer: Trading cryptocurrencies involves significant risk. TITAN is a tool designed to assist in trading and does not guarantee profits.*
