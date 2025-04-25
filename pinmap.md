### 🛞 Left Wheel Pin Map

| Signal | `board.Dxx` | Actual `IOxx` | Notes                   |
|--------|-------------|---------------|-------------------------|
| PWM    | `board.D13` | `IO11`        | Confirmed functional    |
| DIR    | `board.D9`  | `IO1`         | Forward = HIGH          |
| STOP   | `board.D10` | `IO3`         | ESC Enable, HIGH = on   |
| BRAKE  | `board.D6`  | `IO38`        | Brake Active = HIGH     |
| PULSE  | `board.D12` | `IO10`        | ✅ Confirmed pulse input |

### 🛞 Right Wheel Pin Map

| Signal | `board.Dxx` | Actual `IOxx` | Notes                   |
|--------|-------------|---------------|-------------------------|
| PWM    | `board.D19` | `IO5`         | Confirmed functional    |
| DIR    | `board.D16` | `IO14`        | Forward = LOW           |
| STOP   | `board.D17` | `IO12`        | ESC Enable, HIGH = on   |
| BRAKE  | `board.D15` | `IO18`        | Brake Active = HIGH     |
| PULSE  | `board.D14` | `IO6`         | ✅ Confirmed pulse input |
