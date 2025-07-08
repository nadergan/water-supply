#!/usr/bin/env python3
"""
Debug the Q20/Q0 calculation with specific input: (0,80), (456,40)
"""

def calculated_samples(points):
    """
    Calculate Q0 and Q20 based on the provided points.
    """
    y1 = points[0][1]  # 80
    x2 = points[1][0]  # 456
    y2 = points[1][1]  # 40

    print(f"Input points: {points}")
    print(f"y1 (first pressure): {y1}")
    print(f"x2 (second flow): {x2}")
    print(f"y2 (second pressure): {y2}")
    
    k = (x2) / ((y1 - y2) ** (1.0 / 1.85))
    print(f"k coefficient: {k}")
    
    Q0 = int(k * (y1 ** (1.0 / 1.85)))
    Q20 = int(k * ((y1 - 20) ** (1.0 / 1.85)))
    
    print(f"Q0 calculation: k * (y1^(1/1.85)) = {k} * ({y1}^(1/1.85)) = {Q0}")
    print(f"Q20 calculation: k * ((y1-20)^(1/1.85)) = {k} * ({y1-20}^(1/1.85)) = {Q20}")
    
    result = [[Q20, 20], [Q0, 0]]
    print(f"Returned points: {result}")
    return result

# Test with your specific data: (0,80), (456,40)
first_line_points = [(0.0, 80.0), (456.0, 40.0)]
print("🔍 Debugging Q20/Q0 calculation with (0,80), (456,40):")
calculated_points = calculated_samples(first_line_points)

print(f"\n📊 Final points structure:")
final_points = first_line_points + calculated_points
for i, point in enumerate(final_points):
    print(f"  Point {i}: {point}")

print(f"\n🎯 X-axis limits:")
q20_value = calculated_points[0][0]  # Q20 point
q0_value = calculated_points[1][0]   # Q0 point

print(f"Q20 point: ({q20_value}, 20)")
print(f"Q0 point: ({q0_value}, 0)")
print(f"If X-axis ends at Q20 + 10%: {q20_value * 1.1}")
print(f"If X-axis ends at Q0 + 10%: {q0_value * 1.1}")

# Check if Q20 should be 567
if q20_value == 567:
    print("✅ Q20 matches your expected value of 567")
else:
    print(f"❌ Q20 is {q20_value}, but you expected 567")
    