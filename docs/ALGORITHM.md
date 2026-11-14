# ANALOG-X Field-Campaign Index

## Purpose
The index screens Earth field-campaign conditions for a chosen task. It is not a planetary similarity score, probability, absolute suitability threshold, geological score, landing-safety rating or rover traversability model.

## NASA POWER variables
- T2M: 2-m air temperature (°C)
- T2M_MAX / T2M_MIN: monthly climatological mean daily maximum/minimum 2-m air temperature (°C)
- RH2M: 2-m relative humidity (%)
- WS10M: wind speed at 10 m (m/s)
- PRECTOTCORR: corrected precipitation (mm/day)
- ALLSKY_SFC_SW_DWN: all-sky surface shortwave radiation (kWh/m²/day), requested for solar tasks

Invalid/fill values are treated as missing. If fewer than two sites return valid values, the app reports measurements but does not produce a relative ranking.

## Relative index formulas
Component values are min–max normalized across the successful sites in the current scan. A candidate's score therefore depends on which other candidates were selected.

- **Volcanic geology / sample-context fieldwork:** 65% dryness (55% inverse precipitation + 45% inverse RH) + 35% air-temperature comfort around 22°C.
- **Rover traverse workflow:** 45% dryness + 25% inverse mean 10-m wind + 30% air-temperature comfort around 22°C. This screens human field-campaign conditions only.
- **Wind/dust experiments:** 55% relative 10-m wind exposure + 45% dryness. It does not measure dust emission, deposition or concentration.
- **Thermal equipment trials:** 65% mean monthly diurnal air-temperature range (T2M_MAX minus T2M_MIN) + 35% seasonal span in monthly mean T2M. These are air-temperature proxies, not surface temperature.
- **Solar-powered field operations:** relative NASA POWER ALLSKY_SFC_SW_DWN among successful sites. This is Earth solar resource, not lunar illumination or mission energy feasibility.

## Field-month suggestions
The app ranks monthly climatology values using the selected task formula and suggests the top three months. This is not a weather forecast. Check local forecasts and carry field instruments before deployment.

## Data caveats
NASA POWER is gridded climatology, not an on-site weather station. WS10M is not friction velocity or dust flux; PRECTOTCORR is not water/ice resource availability; T2M is not rock temperature. No geological inference is made from these meteorological variables.
