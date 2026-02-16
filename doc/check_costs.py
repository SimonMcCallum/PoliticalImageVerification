"""
Cost verification script for PIVS briefing document.
Checks all cost figures for internal consistency.
Outputs corrected values for document update.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("PIVS BRIEFING DOCUMENT - COST VERIFICATION")
print("=" * 70)

# ============================================================
# SECTION 1: Catalyst Cloud unit prices (from price list ref 19)
# ============================================================
print("\n--- Catalyst Cloud Unit Prices ---")

c1_c2r4 = 95.05    # $/month - 2 vCPU, 4 GB RAM
c1_c4r8 = 190.09   # $/month - 4 vCPU, 8 GB RAM
obj_storage_geo = 0.10  # $/GiB/month geo-replicated
obj_storage_single = 0.05  # $/GiB/month single-region
block_storage = 0.21  # $/GB/month
load_balancer = 24.62  # $/month
ipv4 = 4.50  # $/month each
data_transfer_out = 0.12  # $/GB

print(f"  c1.c2r4:         ${c1_c2r4}/mo")
print(f"  c1.c4r8:         ${c1_c4r8}/mo")
print(f"  Object (geo):    ${obj_storage_geo}/GiB/mo")
print(f"  Object (single): ${obj_storage_single}/GiB/mo")
print(f"  Block storage:   ${block_storage}/GB/mo")
print(f"  Load balancer:   ${load_balancer}/mo")
print(f"  IPv4:            ${ipv4}/mo each")
print(f"  Data transfer:   ${data_transfer_out}/GB out")

# ============================================================
# SECTION 2: Monthly hosting breakdown (para 32)
# ============================================================
print("\n--- Monthly Hosting Breakdown (para 32) ---")

# a. Application compute: 2 app servers + 1 worker = 3 instances
compute_low = 3 * c1_c2r4   # $285.15
compute_high = 3 * c1_c4r8  # $570.27

# Document's rounded values for each sub-item
doc_compute_low, doc_compute_high = 285, 570
doc_db_low, doc_db_high = 180, 360
doc_storage_low, doc_storage_high = 5, 20
doc_network_low, doc_network_high = 75, 150
doc_overhead_low, doc_overhead_high = 80, 165

print(f"  a. Compute:   ${doc_compute_low} - ${doc_compute_high}")
print(f"  b. Database:  ${doc_db_low} - ${doc_db_high}")
print(f"  c. Storage:   ${doc_storage_low} - ${doc_storage_high}")
print(f"  d. Network:   ${doc_network_low} - ${doc_network_high}")
print(f"  e. Overhead:  ${doc_overhead_low} - ${doc_overhead_high}")

line_items_low = doc_compute_low + doc_db_low + doc_storage_low + doc_network_low + doc_overhead_low
line_items_high = doc_compute_high + doc_db_high + doc_storage_high + doc_network_high + doc_overhead_high

print(f"\n  LINE ITEMS SUM:       ${line_items_low} - ${line_items_high}/mo")
print(f"  DOCUMENT CLAIMS:      $1,000 - $2,500/mo")
print(f"  DISCREPANCY LOW:      ${1000 - line_items_low} (doc is ${1000 - line_items_low} higher)")
print(f"  DISCREPANCY HIGH:     ${2500 - line_items_high} (doc is ${2500 - line_items_high} higher)")

# Verify the 15% overhead calculation
pre_overhead_low = doc_compute_low + doc_db_low + doc_storage_low + doc_network_low
pre_overhead_high = doc_compute_high + doc_db_high + doc_storage_high + doc_network_high
calc_overhead_low = round(pre_overhead_low * 0.15)
calc_overhead_high = round(pre_overhead_high * 0.15)
print(f"\n  15% overhead check:")
print(f"    Low:  15% of ${pre_overhead_low} = ${calc_overhead_low} (doc: ${doc_overhead_low})")
print(f"    High: 15% of ${pre_overhead_high} = ${calc_overhead_high} (doc: ${doc_overhead_high})")

# ============================================================
# SECTION 3: Corrected values
# ============================================================
MONTHS = 8
GST = 0.15

print("\n\n" + "=" * 70)
print("CORRECTED VALUES FOR DOCUMENT")
print("=" * 70)

# Use document's line items as source of truth
corrected_monthly_low = line_items_low    # $625
corrected_monthly_high = line_items_high  # $1,265

# For presentation, round to clean numbers
presented_monthly_low = 625
presented_monthly_high = 1275  # slight round-up for conservative estimate

hosting_8mo_low = presented_monthly_low * MONTHS
hosting_8mo_high = presented_monthly_high * MONTHS

print(f"\n  Monthly hosting (from line items):  ${presented_monthly_low} - ${presented_monthly_high}")
print(f"  8-month hosting:                    ${hosting_8mo_low:,} - ${hosting_8mo_high:,}")

# GST on hosting
gst_monthly_low = round(presented_monthly_low * (1 + GST))
gst_monthly_high = round(presented_monthly_high * (1 + GST))
gst_8mo_low = gst_monthly_low * MONTHS
gst_8mo_high = gst_monthly_high * MONTHS
print(f"  Monthly incl GST:                   ${gst_monthly_low:,} - ${gst_monthly_high:,}")
print(f"  8-month incl GST:                   ${gst_8mo_low:,} - ${gst_8mo_high:,}")

# Cost table items
security_audit = (20000, 40000)
acceptance_test = (10000, 20000)
load_test = (5000, 10000)
wcag_audit = (1000, 2000)
pia = (0, 5000)
hosting = (hosting_8mo_low, hosting_8mo_high)

items = [
    ("Security audit and penetration test", security_audit),
    ("Acceptance and integration testing", acceptance_test),
    ("Load and stress testing", load_test),
    ("WCAG accessibility audit", wcag_audit),
    ("Privacy Impact Assessment", pia),
    (f"Infrastructure hosting ({MONTHS} months)", hosting),
]

total_low = sum(v[0] for _, v in items)
total_high = sum(v[1] for _, v in items)

print(f"\n  --- Cost Table ---")
for name, (low, high) in items:
    print(f"  {name:45s} ${low:>7,} - ${high:>7,}")
print(f"  {'':45s} {'':>7s}   {'':>7s}")
print(f"  {'TOTAL':45s} ${total_low:>7,} - ${total_high:>7,}")

# Rounded total for exec summary
print(f"\n  Exact table total:      ${total_low:,} - ${total_high:,}")
print(f"  Rounded for exec summ:  $40,000 - ${round(total_high, -3):,}")

# ============================================================
# SECTION 4: Appendix D corrected
# ============================================================
print(f"\n  --- Appendix D (Transfer Approach) ---")
ip_cost = 20000
# Testing items (acceptance + load + WCAG + PIA)
testing_low = acceptance_test[0] + load_test[0] + wcag_audit[0] + pia[0]
testing_high = acceptance_test[1] + load_test[1] + wcag_audit[1] + pia[1]

print(f"  IP acquisition:                     ${ip_cost:,}")
print(f"  Hosting ({MONTHS} months):                   ${hosting_8mo_low:,} - ${hosting_8mo_high:,}")
print(f"  Security audit & pen testing:        ${security_audit[0]:,} - ${security_audit[1]:,}")
print(f"  Testing (accept+load+WCAG+PIA):      ${testing_low:,} - ${testing_high:,}")
print(f"  Operational subtotal:                ${total_low:,} - ${total_high:,}")
print(f"  TOTAL with IP:                       ${ip_cost + total_low:,} - ${ip_cost + total_high:,}")

# ============================================================
# SECTION 5: All cost mentions - current vs corrected
# ============================================================
print("\n\n" + "=" * 70)
print("DOCUMENT CHANGES NEEDED")
print("=" * 70)

changes = [
    ("Para 3 (Proposal)",           "$40,000-$100,000",                f"$40,000-${round(total_high,-3):,}", "Rounded from table"),
    ("Para 7 (Exec Summary)",       "$40,000-$100,000",                f"$40,000-${round(total_high,-3):,}", "Rounded from table"),
    ("Para 7",                      "intial",                          "initial", "Typo fix"),
    ("Para 29",                     "intial",                          "initial", "Typo fix"),
    ("Table: hosting row",          "$1,000-$2,500/month",             f"${presented_monthly_low}-${presented_monthly_high}/month", "Match line items"),
    ("Table: hosting 8-mo",         "$8,000-$20,000",                  f"${hosting_8mo_low:,}-${hosting_8mo_high:,}", "Match monthly x 8"),
    ("Table: total",                "$44,000-$99,000",                 f"${total_low:,}-${total_high:,}", "Sum of items"),
    ("Para 32",                     "$1,000-$2,500",                   f"${presented_monthly_low}-${presented_monthly_high}", "Match line items"),
    ("Para 33 GST monthly",         "$1,150-$2,875/month",             f"${gst_monthly_low:,}-${gst_monthly_high:,}/month", "Recalculated"),
    ("Para 33 GST 8-month",         "$9,200-$23,000",                  f"${gst_8mo_low:,}-${gst_8mo_high:,}", "Recalculated"),
    ("Para 46 (Recommendations)",   "$40,000-$10,000",                 f"$40,000-${round(total_high,-3):,}", "TYPO FIX + align"),
    ("Appendix D table",            "$60,000-$110,000 hosting+deploy", f"${total_low:,}-${total_high:,}", "Match cost table"),
    ("Appendix D text",             "$60,000-$110,000",                f"${total_low:,}-${total_high:,}", "Match cost table"),
    ("Appendix D text hosting",     "$8,000-$20,000",                  f"${hosting_8mo_low:,}-${hosting_8mo_high:,}", "Corrected"),
    ("Appendix D text security",    "$30,000-$50,000",                 f"${security_audit[0]:,}-${security_audit[1]:,}", "Match table"),
    ("Appendix D text testing",     "$20,000-$40,000",                 f"${testing_low:,}-${testing_high:,}", "Match table items"),
    ("Appendix D",                  "aquisition",                      "acquisition", "Typo fix"),
]

print(f"\n  {'Location':<30s} {'Current':<35s} {'Corrected':<30s} {'Reason'}")
print(f"  {'-'*30} {'-'*35} {'-'*30} {'-'*20}")
for loc, current, corrected, reason in changes:
    marker = " ***" if current != corrected else ""
    print(f"  {loc:<30s} {current:<35s} {corrected:<30s} {reason}{marker}")

print(f"\n\nTotal changes needed: {sum(1 for _, c, n, _ in changes if c != n)}")

print("\n" + "=" * 70)
print("SCRIPT COMPLETE")
print("=" * 70)
