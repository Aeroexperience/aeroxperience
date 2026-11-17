# Squawk airport taxi data

One small JSON file per airport (`K/KSAN.json`, `E/EGLL.json`, ...) with the taxi network Squawk uses to give real taxi instructions.

- Taxiways, nodes and gates: FlightGear `groundnet.xml` files from https://github.com/mherweg/Airports, which were converted from X-Plane 11 `apt.dat` data (2017).
- Runway ends: OurAirports `runways.csv` (https://github.com/davidmegginson/ourairports-data).

Fields: `n` nodes `[lat, lon, flags (1 = on runway, 2 = hold point), runway index]`, `e` edges `[node, node, taxiway name index, is pushback]`, `t` taxiway names, `p` parking `[name, node, pushback node]`, `r` runways `[le, he, le lat, le lon, he lat, he lon]`.

Some airports have changed since 2017, so a few routes may not match the current layout.

## Frequencies

`freq/<first letter>.json` maps each airport to its real COM frequencies `[type, description, MHz]` from OurAirports `airport-frequencies.csv` (tower, ground, clearance, ATIS/AWOS, approach, departure, center). Squawk picks the one for your runway when an airport lists several.

## US frequencies (FAA NASR)

For US airports, `freq/*.json` comes from the FAA's 28-day NASR subscription (FRQ and ATC CSV groups, cycle effective 2026-10-29). This is the same data the Chart Supplement is printed from, and it is public domain. US entries look like `{"f": [[type, description, MHz, sector?], ...], "t": tower call, "a": approach call, "d": departure call, "h": tower hours}`. Sectors are bearing ranges from the airport plus a low/high altitude band. `DP` and `STAR` entries give the frequency for a specific departure or arrival procedure.

To refresh every 28 days: download `29_Oct_2026_FRQ_CSV.zip` and `..._ATC_CSV.zip` (new date each cycle) from the FAA NASR subscription page and run:

    python3 -I squawk/tools/faa_freq.py FRQ.csv ATC_BASE.csv <ourairports freq dir> squawk/airports/freq

Airports outside the US still use OurAirports.
