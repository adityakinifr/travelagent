# Car Rental API Setup Guide

This guide explains how to set up real car rental APIs to replace the mock data in your travel agent.

## Available Car Rental APIs

### 1. Booking.com API (Primary - Recommended)

**Overview**: Booking.com's Demand API provides access to car rental inventory from their extensive network of partners worldwide.

**Coverage**: 
- Global coverage through Booking.com's partner network
- Real-time availability and pricing
- Multiple car rental suppliers
- Currently in early access pilot phase (Q2 2025 general availability)

**Setup Steps**:
1. Visit [Booking.com Developer Portal](https://developers.booking.com/)
2. Contact Booking.com's partnerships team for early access
3. Get your API key and affiliate ID
4. Add to `.env`: 
   - `BOOKING_API_KEY=your_booking_api_key_here`
   - `BOOKING_AFFILIATE_ID=your_booking_affiliate_id_here`

**API Endpoint**: `https://distribution-xml.booking.com/2.5/json/cars/search`

**Authentication**: Requires both API key (Bearer token) and Affiliate ID (X-Affiliate-Id header)

### 2. CarTrawler API (Secondary)

**Overview**: CarTrawler connects over 2,500 travel agents with local car rental suppliers across 45,000 locations in 185 countries.

**Coverage**: 
- 45,000+ locations worldwide
- 185 countries
- 2,500+ travel agents and airlines

**Setup Steps**:
1. Visit [CarTrawler Developer Portal](https://www.cartrawler.com/ct/developers/)
2. Sign up for a developer account
3. Request API access
4. Get your API key
5. Add to `.env`: `CARTRAWLER_API_KEY=your_key_here`

**API Endpoint**: `https://api.cartrawler.com/v1/cars`

### 3. Rentalcars.com API (Tertiary)

**Overview**: One of the largest car rental providers operating in 60,000+ locations across 165 countries.

**Coverage**:
- 60,000+ locations worldwide
- 165 countries
- Major car rental companies

**Setup Steps**:
1. Visit [Rentalcars.com Partner Network](https://www.rentalcars.com/en/partner-network/)
2. Apply for partnership
3. Get API credentials
4. Add to `.env`: `RENTALCARS_API_KEY=your_key_here`

**API Endpoint**: `https://api.rentalcars.com/v1/search`

### 4. Alternative Options

#### Skyscanner Car Hire API
- **Website**: [Skyscanner for Business](https://www.skyscanner.net/business/)
- **Features**: Global car rental marketplace data
- **Coverage**: Worldwide

#### Priceline Partner Network API
- **Website**: [Priceline Partner Network](https://www.priceline.com/partner-network/)
- **Features**: Dynamic car rental data for 180+ countries
- **Coverage**: 180+ countries

#### Trawex Car API
- **Website**: [Trawex Car API](https://www.trawex.com/car-api-providers.php)
- **Features**: Live rates and availability data
- **Coverage**: 70+ countries

## Implementation Priority

The system tries APIs in this order:

1. **Booking.com API** (Primary - global coverage, real-time data)
2. **CarTrawler API** (Secondary - comprehensive coverage)
3. **Rentalcars.com API** (Tertiary - large coverage)
4. **Amadeus Mock Data** (Fallback - realistic mock data)

## Environment Configuration

Add these to your `.env` file:

```bash
# Car Rental APIs
BOOKING_API_KEY=your_booking_api_key_here
BOOKING_AFFILIATE_ID=your_booking_affiliate_id_here
CARTRAWLER_API_KEY=your_cartrawler_api_key_here
RENTALCARS_API_KEY=your_rentalcars_api_key_here
```

## Testing

Run the debug script to test car rental APIs:

```bash
python debug_amadeus.py
```

Or test the full system:

```bash
python test_today.py
```

## API Response Format

The system expects car rental APIs to return data in this format:

```json
{
  "cars": [
    {
      "supplier": "Hertz",
      "vehicleType": "Economy Car",
      "pricePerDay": 45,
      "totalPrice": 315,
      "features": ["Automatic", "AC", "4 doors"]
    }
  ]
}
```

## Benefits of Real APIs

- ✅ **Real-time pricing**: Current market rates
- ✅ **Live availability**: Actual car availability
- ✅ **Accurate data**: Real rental companies and locations
- ✅ **Global coverage**: Worldwide car rental options
- ✅ **Professional quality**: Production-ready data

## Sample Output

```
API Key Status:
  Booking.com API Key: ✓ Configured
  Booking.com Affiliate ID: ✓ Configured
  CarTrawler API Key: ✗ Not configured
  Rentalcars.com API Key: ✗ Not configured

🔍 Testing car rental search...
Searching car rentals via Booking.com in: PAR
✅ Found 5 car rentals from Booking.com
```

## Fallback System

If no real APIs are configured or available:
- System uses realistic mock data
- Location-based pricing (US: $45, Europe: $50, Asia: $35)
- Dynamic pricing based on rental duration
- Multiple car types and companies

## Support

For API-specific issues:
- **Booking.com**: Contact their partnerships team or use their developer support
- **CarTrawler**: Contact their developer support
- **Rentalcars.com**: Use their partner support
- **General**: Check the debug script output for detailed error messages

## Cost Considerations

- Most car rental APIs require partnership agreements
- Some may have minimum volume requirements
- Consider your usage volume when choosing providers
- Mock data is free and always available as fallback
