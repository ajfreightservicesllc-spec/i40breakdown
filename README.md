# I-40 Breakdown

Emergency truck, trailer, diesel & RV repair directory along Interstate 40.

## Site Details

- **Live URL:** https://i40breakdown.web.app
- **Custom Domain:** i40breakdown.com (pending DNS setup)
- **GA Tag:** G-M0PYD8479W
- **Firebase Project:** aiansweragency-main
- **Firebase Hosting Site:** i40breakdown

## Features

- Emergency repair shop search across 8 states (CA, AZ, NM, TX, OK, AR, TN, NC)
- Location-based search with geolocation
- Service filters (24/7, mobile, truck specialist, RV, reefer, tire, engine, trailer, brakes, electrical)
- Sort by distance, rating, reviews, or name
- Direct call, map, and website links for each shop
- Responsive design with dark blue/cyan theme
- Animated hero with honking truck

## Shop Data

- 664 total emergency repair shops
- Real phone numbers and website links
- Star ratings and review counts
- Service specialties tagged for each location

## Development

- Single-page HTML file with embedded CSS and JavaScript
- No build process required
- Pure vanilla JavaScript
- Firebase Hosting deployment

## Deployment

```bash
firebase deploy -c firebase_i40.json --only hosting:i40breakdown --project aiansweragency-main
```

## Notes

- GA data collection begins 24-48 hours after deployment
- Site is live and operational
- All 664 shops use data from integrated database
- Color scheme: Dark blue (#0a1428) with cyan accents (#00d4ff)
