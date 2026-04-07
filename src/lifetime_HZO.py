# 1. Define default parameters for lifetime analysis
endurance = 1e9          # Intrinsic endurance (cycles)
c_mem_mb = 2             # Memory capacity in MB
w_data_bits = 64         # Array data width in bits
t_write_per_day = 1e5    # Potential write traffic per day

# 2. Convert units to be consistent (Bytes)
c_mem_bytes = c_mem_mb * 1024 * 1024
w_data_bytes = w_data_bits / 8

print(f"--- Calculating Lifetime for {c_mem_mb}MB FeFET Array ---")

# 3. Calculate lifetime in days using Eq(9): Lifetime = (Endurance * C_mem) / (t_write * W_data)
# C_mem / W_data gives the total number of addressable words in the array
lifetime_days = (endurance * c_mem_bytes) / (t_write_per_day * w_data_bytes)

# 4. Convert days to years and apply the 5-year strict cap
lifetime_years = lifetime_days / 365.25
lifetime_cap_years = 5.0

final_lifetime_years = min(lifetime_years, lifetime_cap_years)

# Output the results
print(f"Theoretical Lifetime: {lifetime_years:.2e} years")
print(f"Final Capped Lifetime: {final_lifetime_years:.2f} years")