"""
Simple test for feasibility system
"""

from feasibility_checker import FeasibilityChecker

def test_basic_functionality():
    """Test basic feasibility checker functionality"""
    
    print("🔍 Testing Basic Feasibility Functionality")
    print("=" * 50)
    
    checker = FeasibilityChecker()
    
    # Test budget parsing
    print("Testing budget parsing...")
    test_budgets = ["$1200", "$500", "1000", "$1.5k", "200-400"]
    
    for budget in test_budgets:
        parsed = checker._parse_budget(budget)
        print(f"   '{budget}' -> ${parsed}")
    
    # Test date parsing
    print("\nTesting date parsing...")
    seasons = ["summer", "winter", "spring", "fall"]
    
    for season in seasons:
        dep, ret = checker._parse_travel_dates(season)
        print(f"   {season} -> {dep} to {ret}")
    
    # Test budget allocation
    print("\nTesting budget allocation...")
    test_cases = [
        ("$1000", "leisure"),
        ("$1500", "business"),
        ("$800", "family_with_kids")
    ]
    
    for budget, traveler_type in test_cases:
        flight_budget = checker._get_flight_budget_limit(budget, traveler_type)
        hotel_budget = checker._get_hotel_budget_limit(budget, traveler_type)
        print(f"   {budget} {traveler_type}: Flight ${flight_budget:.0f}, Hotel ${hotel_budget:.0f}")
    
    print("\n✅ Basic functionality tests completed!")

if __name__ == "__main__":
    test_basic_functionality()
