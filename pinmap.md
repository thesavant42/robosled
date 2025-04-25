# Pin Map

## Left Wheel

Function        | Pin              | Notes
PWM             | board.D13 / IO13 | Speed control via PWM
DIR (Direction) | board.D9 / IO9   | HIGH = Forward
STOP (Enable)   | board.D10 / IO10 | Must be HIGH to run
BRAKE           | board.D6 / IO6   | HIGH = Brakes engaged
SPEED           | board.D12 / IO12 | ✅ Confirmed using countio
FWD Logic       | True (HIGH)      | DIR = HIGH means forward

## Right Wheel

Function         | Pin              | Notes
PWM              | board.D19 / IO19 | Speed control via PWM
DIR (Direction)  | board.D16 / IO16 | LOW = Forward
STOP (Enable)    | board.D17 / IO17 | Must be HIGH to run
BRAKE            | board.D15 / IO15 | HIGH = Brakes engaged
PULSE            | board.D14 / IO14 | ✅ Confirmed using countio
FWD Logic        | False (LOW)      | DIR = LOW means forward
