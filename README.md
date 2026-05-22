# SCRF // Seller Suite

> AI-powered reseller workstation for collectibles flippers.  
> Pricing intelligence, eBay listings, and social copy, one click.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Powered%20by-Claude%20AI-blueviolet?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey?style=flat-square)

---

## What It Does

You find an item. You drop it in. Claude tells you whether to flip it, what to charge, and writes every word you need to sell it: listing title, full description, and platform-specific social copy for Instagram, TikTok, Facebook, Twitter/X, and your Skip blog.

No subscriptions. No web app. Runs on your machine.

---

## Features

- **📷 Vision-powered identification** — upload a photo and Claude reads labels, condition, variants, and serial numbers automatically
- **⚡ Flip verdict** — FLIP NOW / HOLD / BUNDLE / GRADE IT / PASS with estimated ROI
- **💰 Three-tier pricing** — floor, recommended sweet spot, and graded ceiling
- **📝 Ready-to-paste listings** — SEO-optimized title + full description for eBay, Hello Skip, Mercari, Facebook Marketplace, OfferUp
- **📱 Social funnel** — five platform-specific posts generated in one call
- **🔒 API key stays local** — never stored to disk, session-only

---

## Built For

[Starchild Rare Finds] — a DFW-based collectibles resale business specializing in Pokémon cards, Yu-Gi-Oh, vinyl records, VHS, retro gaming, antiques, and general collectibles.

Developed by **[Starchild Rare Finds.]

---

## Requirements

- Python 3.8+
- An [Anthropic API key](https://console.anthropic.com) (Claude Sonnet — ~$0.01–0.03 per analysis)
- No additional pip installs — uses stdlib only (`tkinter`, `urllib`, `base64`, `json`)

---

## Setup

```bash
git clone https://github.com/SCRF-IT/scrf-seller-suite.git
cd scrf-seller-suite
python scrf_seller_suite.pyw
```

1. Paste your Anthropic API key and hit **SAVE**
2. Fill in item details (or upload a photo and let Claude identify it)
3. Hit **⚡ ANALYZE + GENERATE EVERYTHING**

---

## Photo Upload

Attach a `.jpg`, `.png`, or `.webp` photo of your item before analyzing. Claude's vision model will:

- Identify the exact item (card name, game title, record pressing, etc.)
- Assess visible condition
- Read labels, stamps, serial numbers, and edition markings
- Factor all of it into pricing and copy

Works especially well for Pokémon cards, cartridges, vinyl, and vintage electronics.

---

## Supported Platforms

| Platform | Listing | Social Copy |
|----------|---------|-------------|
| eBay | ✅ | — |
| Hello Skip | ✅ | ✅ Blog post |
| Facebook Marketplace | ✅ | ✅ |
| Mercari | ✅ | — |
| OfferUp | ✅ | — |
| Instagram | — | ✅ |
| TikTok | — | ✅ |
| Twitter / X | — | ✅ |

---

## License

MIT — free to use, fork, and adapt. Attribution appreciated.

---

*Built with Python + Claude by [Starchild Rare Finds]*
