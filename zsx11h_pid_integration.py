# /code/zsx11h_test_harness.py
# Manual ZS-X11H motor tester with dynamic config, auto‐tuning PID, and enhanced menu flow
# Author: savant42

import board
import digitalio
import pwmio
import time
import countio

from config import MOTOR_CONFIG, RAMP_MIN_DUTY, RAMP_STEP, RAMP_DELAY
from PID_CPY import PID

# Load devices from configuration
DEVICES = list(MOTOR_CONFIG.values())

# Track resources to avoid reinit errors
last_pwm = None
last_dir = None
last_stop = None
last_brake = None

# === Scan Parameters ===
SCAN_DUTY = 60       # % duty for open-loop scan
SCAN_INTERVAL = 0.5   # seconds between samples
SCAN_DURATION = 10    # total seconds per scan

# === Stats Storage ===
LAST_STATS = {}  # name -> (avg_pps, std_pps, avg_rpm)

# === PID Parameters ===
PID_PARAMS = {'Kp': 1.0, 'Ki': 0.0, 'Kd': 0.0}
SETPOINT = None   # target pulses/sec for closed-loop tests

# === Setup IO ===
def setup_device(device):
    global last_pwm, last_dir, last_stop, last_brake
    print(f"\nDEVICE: {device['name']}")
    for key in ['PWM','DIR','STOP','BRAKE','PULSE']:
        print(f"  {key}: {device[key]}")
    for res in (last_pwm,last_dir,last_stop,last_brake):
        if res and hasattr(res,'deinit'):
            res.deinit()
    pwm = pwmio.PWMOut(device['PWM'], frequency=2000, duty_cycle=0)
    last_pwm = pwm
    dir_pin = digitalio.DigitalInOut(device['DIR'])
    dir_pin.direction = digitalio.Direction.OUTPUT
    dir_pin.value = device['FWD'] if device['DESIRED_DIR']=='FWD' else not device['FWD']
    last_dir = dir_pin
    stop = digitalio.DigitalInOut(device['STOP'])
    stop.direction = digitalio.Direction.OUTPUT; stop.value = False; last_stop = stop
    brake = digitalio.DigitalInOut(device['BRAKE'])
    brake.direction = digitalio.Direction.OUTPUT; brake.value = True; last_brake = brake
    init_dir = 'FORWARD' if dir_pin.value==device['FWD'] else 'REVERSE'
    init_brake='ENGAGED' if brake.value else 'RELEASED'
    init_stop='ENABLED' if stop.value else 'DISABLED'
    print(f"[INIT] {device['name']} - DIR: {init_dir}, BRAKE: {init_brake}, STOP: {init_stop}")
    return pwm,dir_pin,stop,brake,device['PULSE']

# === PWM Ramp Logic ===
def pwm_ramp(pwm, stop, brake):
    if brake.value: brake.value=False
    stop.value=True
    duty = RAMP_MIN_DUTY
    print(f"[RAMP] Starting from {duty}% to 100% in {RAMP_STEP}% steps")
    while duty <= 100:
        pwm.duty_cycle = int(duty * 655.35)
        print(f" PWM {duty}%")
        time.sleep(RAMP_DELAY)
        duty += RAMP_STEP
    print("[RAMP] Reversing ramp down")
    duty = 100
    while duty >= RAMP_MIN_DUTY:
        pwm.duty_cycle = int(duty * 655.35)
        print(f" PWM {duty}%")
        time.sleep(RAMP_DELAY)
        duty -= RAMP_STEP
    pwm.duty_cycle = 0
    brake.value = True; stop.value = False
    print("[RAMP] Done. Motor stopped and brake engaged.")

# === Pulse Scan ===
def sniff_pulse_scan(device):
    global SCAN_DUTY,SCAN_INTERVAL,SCAN_DURATION,LAST_STATS
    print(f"\n🔍 Scan {device['name']} @ {SCAN_DUTY}% for {SCAN_DURATION}s, interval {SCAN_INTERVAL}s")
    pwm=last_pwm; stop=last_stop; brake=last_brake
    brake.value=False; stop.value=True; pwm.duty_cycle=0; time.sleep(0.2)
    pwm.duty_cycle=int(SCAN_DUTY*655.35)
    counter=countio.Counter(device['PULSE'],edge=countio.Edge.RISE)
    samples=[]; start=time.monotonic(); last=counter.count
    while time.monotonic()-start<SCAN_DURATION:
        now=counter.count; delta=now-last
        if delta>0:
            samples.append(delta); print(f" 🌀 {delta} edges (total={now})"); last=now
        time.sleep(SCAN_INTERVAL)
    pwm.duty_cycle=0; brake.value=True; stop.value=False; counter.deinit()
    if samples:
        pps=[d/SCAN_INTERVAL for d in samples]
        avg_pps=sum(pps)/len(pps)
        std_pps=(sum((x-avg_pps)**2 for x in pps)/len(pps))**0.5
        # simple RPM: assume device['PULSES_PER_REV'] or default 20
        ppr=device.get('PULSES_PER_REV',20)
        avg_rpm=avg_pps/ppr*60
        LAST_STATS[device['name']]=(avg_pps,std_pps,avg_rpm)
        print(f"[DONE] Avg={avg_pps:.1f}pps ({avg_rpm:.1f}RPM), Std={std_pps:.1f}pps over {len(pps)} samples")
    else:
        print("[DONE] No edges detected.")

# === Capture for Auto-Tune ===
def run_pid_capture(device,pwm,dir_pin,stop,brake):
    """
    Run a short closed-loop test (P-only) to capture error crossings for oscillation detection.
    Returns timestamped error list.
    """
    if SETPOINT is None:
        print("❌ Set SETPOINT first."); return []
    # Zero I and D
    Ki, Kd = PID_PARAMS['Ki'], PID_PARAMS['Kd']
    PID_PARAMS['Ki'], PID_PARAMS['Kd'] = 0, 0
    pid = PID(Kp=PID_PARAMS['Kp'], Ki=0, Kd=0, setpoint=SETPOINT, sample_time=SCAN_INTERVAL, output_limits=(0,100))
    # Prep motor
    brake.value=False; stop.value=True; pwm.duty_cycle=0; time.sleep(0.2)
    counter=countio.Counter(device['PULSE'],edge=countio.Edge.RISE)
    errs=[]; last_count=counter.count; start=time.monotonic()
    while time.monotonic()-start < SCAN_DURATION:
        now=counter.count; delta=now-last_count; meas=delta/SCAN_INTERVAL
        err=SETPOINT - meas; errs.append((time.monotonic()-start,err))
        out=pid(meas); pwm.duty_cycle=int(out*655.35)
        last_count=now; time.sleep(SCAN_INTERVAL)
    pwm.duty_cycle=0; brake.value=True; stop.value=False; counter.deinit()
    PID_PARAMS['Ki'], PID_PARAMS['Kd'] = Ki, Kd
    return errs

# === Auto-Tune ===
def auto_tune_pid(device,pwm,dir_pin,stop,brake):
    global PID_PARAMS, SETPOINT
    print("\n🤖 Starting PID auto-tuner...")
    if SETPOINT is None:
        print("❌ Define SETPOINT in main menu first."); return
    # Sweep Kp until oscillation detected
    Ku, Pu = None, None
    for kp in range(1, 101, 5):
        PID_PARAMS['Kp']=kp; print(f" Testing Kp={kp}")
        errs = run_pid_capture(device,pwm,dir_pin,stop,brake)
        # detect zero crossings
        crossings=[]
        for i in range(1,len(errs)):
            if errs[i-1][1]*errs[i][1] < 0:
                crossings.append(errs[i][0])
        if len(crossings)>=6:
            # measure last period
            Pu = crossings[-1] - crossings[-3]
            Ku = kp
            print(f" Oscillation at Kp={Ku}, Pu={Pu:.2f}s")
            break
    if not Ku:
        print("❌ Could not find Ku; try larger sweep range."); return
    # Ziegler-Nichols tuning
    newKp = 0.6*Ku
    newKi = 2*newKp/Pu
    newKd = newKp*Pu/8
    PID_PARAMS.update({'Kp':newKp,'Ki':newKi,'Kd':newKd})
    print(f"🎯 Auto-tuned PID -> Kp={newKp:.3f}, Ki={newKi:.3f}, Kd={newKd:.3f}")

# === Wheel Test Menu ===
def wheel_test_menu(device,pwm,dir_pin,stop,brake,pulse):
    while True:
        print(f"\n{device['name']} Test Menu:")
        print(" [1] Toggle BRAKE")
        print(" [2] Toggle DIR")
        print(" [3] Toggle STOP (ESC)")
        print(" [4] PWM Ramp Test")
        print(" [5] Pulse Scan")
        print(" [6] Config scan params")
        print(" [7] Configure PID constants")
        print(" [8] Suggest PID constants")
        print(" [9] Auto-tune PID")
        print(" [10] Back to main menu")
        c=input("> ").strip()
        if c=='1': brake.value=not brake.value; print(f"[BRAKE] {'ENGAGED' if brake.value else 'RELEASED'}")
        elif c=='2': dir_pin.value=not dir_pin.value; print(f"[DIR] Now {'FORWARD' if dir_pin.value==device['FWD'] else 'REVERSE'}")
        elif c=='3': stop.value=not stop.value; print(f"[STOP] ESC {'ENABLED' if stop.value else 'DISABLED'}")
        elif c=='4': pwm_ramp(pwm,stop,brake)
        elif c=='5': sniff_pulse_scan(device)
        elif c=='6':
            try: SCAN_DUTY=float(input("Scan duty %: ")); SCAN_INTERVAL=float(input("Scan interval s: ")); SCAN_DURATION=float(input("Scan duration s: "))
            except: print("❌ Invalid scan params"); continue
            print(f"Updated scan: duty={SCAN_DUTY}%, interval={SCAN_INTERVAL}s, duration={SCAN_DURATION}s")
        elif c=='7':
            try: PID_PARAMS['Kp']=float(input("Enter Kp: ")); PID_PARAMS['Ki']=float(input("Enter Ki: ")); PID_PARAMS['Kd']=float(input("Enter Kd: "))
            except: print("❌ Invalid PID input"); continue
            print(f"PID set: {PID_PARAMS}")
        elif c=='8':
            if device['name'] in LAST_STATS:
                avg=LAST_STATS[device['name']][0]; Kp=1/(avg/SCAN_DUTY); Ki=Kp/SCAN_DURATION; Kd=Kp*(SCAN_INTERVAL/2)
                print(f"Suggested PID: Kp={Kp:.3f}, Ki={Ki:.3f}, Kd={Kd:.3f}")
            else: print("❌ Run pulse scan first.")
        elif c=='9': auto_tune_pid(device,pwm,dir_pin,stop,brake)
        elif c=='10': break
        else: print("❌ Invalid selection.")

# === Main Menu ===
if __name__=='__main__':
    while True:
        print("\nMain Menu — Select device:")
        for i,dev in enumerate(DEVICES,1): print(f" [{i}] {dev['name']}")
        comp=len(DEVICES)+1; stats=comp+1; setp=stats+1; exit_idx=setp+1
        print(f" [{comp}] Compare last stats")
        print(f" [{stats}] Configure global SETPOINT")
        print(f" [{setp}] Clear SETPOINT")
        print(f" [{exit_idx}] Exit")
        sel=input("> ").strip();
        try: idx=int(sel)
        except: idx=None
        if 1<=idx<=len(DEVICES):
            pwm,dir_pin,stop,brake,pulse=setup_device(DEVICES[idx-1])
            wheel_test_menu(DEVICES[idx-1],pwm,dir_pin,stop,brake,pulse)
        elif idx==comp:
            print("\nLast Stats:")
            for name,(a,s,r) in LAST_STATS.items(): print(f" {name}: Avg={a:.1f}pps, Std={s:.1f}pps, RPM={r:.1f}")
            input("Enter to continue...")
        elif idx==stats:
            try: val=float(input("SETPOINT (pps): ")); SETPOINT=val; print(f"SETPOINT={SETPOINT}")
            except: print("❌ Invalid setpoint")
        elif idx==setp:
            SETPOINT=None; print("SETPOINT cleared")
        elif idx==exit_idx:
            break
        else: print("❌ Invalid selection.")
