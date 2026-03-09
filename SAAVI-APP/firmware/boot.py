# boot.py - run on boot-up
import machine
import micropython

# Optimize memory
micropython.alloc_emergency_exception_buf(100)

print("Boot sequence complete. Starting main application...")
