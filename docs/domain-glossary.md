# Domain Glossary — Oil & Gas Upstream

## Well Operations

| Term | Definition |
|---|---|
| **Wellhead** | Surface equipment at the top of the well |
| **Bottomhole** | The lowest point of the well, near the reservoir |
| **Choke** | Valve controlling flow rate (CHK: 0=closed, 1=fully open) |
| **Workover** | Intervention to restore or improve production |
| **Completion** | Process of making a well ready for production |

## Production Metrics

| Abbreviation | Full Name | Unit | Description |
|---|---|---|---|
| QOIL | Oil volumetric flow rate | Sm3/h | Oil production at standard conditions |
| QGAS | Gas volumetric flow rate | Sm3/h | Gas production at standard conditions |
| QWAT | Water volumetric flow rate | Sm3/h | Water production at standard conditions |
| GOR | Gas-Oil Ratio | Sm3/Sm3 | Indicates reservoir drive mechanism |
| Water Cut | Water fraction | % | QWAT / (QWAT + QOIL) — reservoir maturity |

## Pressures & Temperatures

| Abbreviation | Full Name | Unit |
|---|---|---|
| PBH | Pressure bottomhole | bar |
| PWH | Pressure wellhead | bar |
| PDC | Pressure downstream choke | bar |
| TBH | Temperature bottomhole | K |
| TWH | Temperature wellhead | K |

## Flow Regimes

| Regime | Description |
|---|---|
| **Bubbly** | Gas as small bubbles in liquid — low gas fraction |
| **Slug-Churn** | Alternating gas and liquid slugs — intermediate |
| **Annular** | Gas core with liquid film on walls — high gas fraction |

## Control Strategies (ManyWells)

| Dataset | Boundary | Control | Meaning |
|---|---|---|---|
| sol-1 | Stationary | Open-loop | Stable conditions, no feedback control |
| nsol-1 | Non-stationary | Open-loop | Changing conditions, no adaptation |
| nscl-1 | Non-stationary | Closed-loop | Changing conditions with adaptive control |

## Key Relationships

- QLIQ = QOIL + QWAT (liquid = oil + water)
- QTOT = QLIQ + QGAS + QGL (total includes lift gas)
- Higher water cut → more mature reservoir → declining oil production
- Higher GOR → gas drive dominant → may need gas lift optimization
- Closed-loop control → adaptive choke management → better stability
