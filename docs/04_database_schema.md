# Database Schema

For the 48-hour hackathon, we are utilizing a relational database (PostgreSQL/SQLite) mapped via SQLAlchemy. The schema focuses on the core entities required for AML investigations.

## Entities

### `users`
System users (Compliance Analysts, Managers).
- `id` (PK, UUID)
- `name` (String)
- `email` (String)
- `role` (String)

### `customers`
The subjects of the investigations.
- `id` (PK, UUID)
- `full_name` (String)
- `kyc_status` (String)
- `baseline_risk` (String)

### `accounts`
Bank accounts belonging to customers.
- `id` (PK, UUID)
- `customer_id` (FK)
- `account_number` (String)
- `balance` (Decimal)

### `transactions`
Financial movements.
- `id` (PK, UUID)
- `source_account_id` (FK)
- `destination_account_id` (FK)
- `amount` (Decimal)
- `timestamp` (DateTime)
- `transaction_type` (String)

### `investigations`
Active or historical cases.
- `id` (PK, UUID)
- `customer_id` (FK)
- `assigned_user_id` (FK)
- `status` (String - NEW, IN_PROGRESS, REVIEW, CLOSED)
- `priority` (String)
- `created_at` (DateTime)

### `ai_planner_traces`
Immutable log of how the AI arrived at its conclusions.
- `id` (PK, UUID)
- `investigation_id` (FK)
- `query` (Text)
- `execution_plan` (JSON)
- `evidence_gathered` (JSON)
- `final_recommendation` (String)

## Notes on Graph Data
While the original design specified Neo4j for Graph Intelligence, for the hackathon MVP, basic relationship queries (e.g., shared addresses, shared IP, frequent transfer partners) will be executed via SQL `JOIN`s or Pandas DataFrames to ensure rapid delivery.
