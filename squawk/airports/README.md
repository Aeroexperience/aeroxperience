# Squawk airport taxi data

One small JSON file per airport (`K/KSAN.json`, `E/EGLL.json`, ...) with the taxi network Squawk uses to give real taxi instructions.

- Taxiways, nodes and gates: FlightGear `groundnet.xml` files from https://github.com/mherweg/Airports, which were converted from X-Plane 11 `apt.dat` data (2017).
- Runway ends: OurAirports `runways.csv` (https://github.com/davidmegginson/ourairports-data).

Fields: `n` nodes `[lat, lon, flags (1 = on runway, 2 = hold point), runway index]`, `e` edges `[node, node, taxiway name index, is pushback]`, `t` taxiway names, `p` parking `[name, node, pushback node]`, `r` runways `[le, he, le lat, le lon, he lat, he lon]`.

Some airports have changed since 2017, so a few routes may not match the current layout.

## Frequencies

`freq/<first letter>.json` maps each airport to its real COM frequencies `[type, description, MHz]` from OurAirports `airport-frequencies.csv` (tower, ground, clearance, ATIS/AWOS, approach, departure, center). Squawk picks the one for your runway when an airport lists several.

## Hand-checked frequencies (`freq-verified.json`)

OurAirports is missing some frequencies and has old ones for others. For the airports in `freq-verified.json`, the app uses that file instead. Each list was copied by hand from the current FAA Chart Supplement (cycle effective 2026-10-29, read in ForeFlight). Approach and departure entries can carry a sector: a bearing range from the airport and a low/high altitude band, so the app hands you the frequency for the direction you are flying.

To add an airport, copy its Communications section from the Chart Supplement into the same format. FAA data is public domain.
