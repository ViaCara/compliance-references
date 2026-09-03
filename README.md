# compliance-references

A community-of-practice mirror of UK and EU compliance instruments in machine-readable markdown. Hosted under the ViaCara GitHub org but framed as a shared resource — outside contributors are welcome to PR.

Contains:

- **Statute** (Tier A, automated): UK GDPR, DPA 2018, PECR, DUAA 2025, EU GDPR, EU AI Act, MDR, IVDR, NIS2, PSD2, EAA, Equality Act 2010, Consumer Rights Act 2015, FSMA 2000, FPO 2005, RAO 2001, MLR 2017, UK PSR 2017, UK MDR 2002, UK NIS Regulations 2018, UK PSBAR 2018, Charter of Fundamental Rights, Online Safety Act 2023, Children Act 1989, Children Act 2004, Family Law Reform Act 1969, Children's Wellbeing and Schools Act 2026, Crime and Policing Act 2026, Safeguarding Vulnerable Groups Act 2006, Employment Agencies Act 1973, Conduct of Employment Agencies and Employment Businesses Regulations 2003, Police Act 1997, Police Act 1997 (Criminal Records) Regulations 2002, Rehabilitation of Offenders Act 1974 (Exceptions) Order 1975, Protection of Vulnerable Groups (Scotland) Act 2007, Disclosure (Scotland) Act 2020.
- **Guidance** (Tier B, curated quote anthology): ICO, EDPB, NCSC, MHRA, CMA, DBS, AccessNI, FCA Handbook, W3C WCAG 2.2.
- **Standards** (Tier C, external index only): BACP, UKCP, HCPC, BPS ethics codes; ISO 27001/27701/42001; BSI.

## Attribution

Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

EU statute is redistributed under [Commission Decision 2011/833/EU](https://eur-lex.europa.eu/eli/dec/2011/833/oj) (free reuse with attribution).

WCAG content is redistributed under the [W3C Document License](https://www.w3.org/Consortium/Legal/2015/doc-license).

Proprietary professional and technical standards (BACP, UKCP, HCPC, BPS, ISO, BSI) are **not** redistributed verbatim. The corpus carries pointer-only references with neutral one-sentence descriptions.

## How it works

`build.py` reads `manifest.json`, fetches each source URI via `urllib.request`, runs the appropriate transformer (`lib/transformer_legislation.py` for legislation.gov.uk XHTML, `lib/transformer_eur_lex.py` for EUR-Lex HTML), writes deterministic markdown under `corpus/` with frontmatter recording source URI, revision id and content hash.

Re-running `build.py` against an unchanged source set produces zero file diffs (determinism contract). Drift triggers a CHANGELOG entry and a new content hash.

## For consumers

Pin a tag (`v<YYYY.MM.DD>`), not `main`. Tags are the contract surface. Additions are free; renames/removals ship as a major-prefix tag (`v2.0.0-<date>`).

A reference Python consumer lives in the ViaCara skill at `.claude/skills/compliance-references/consume.py`.

## Schema-evolution policy

- Additions to manifest/frontmatter are free.
- Renames or removals require a major prefix (`v2.0.0-<date>`).
- Consumers default to the latest matching-major tag.

## Tiered sourcing

| Tier | Authority | How | Licence |
|---|---|---|---|
| A | Statute, binding | Automated fetch from legislation.gov.uk + EUR-Lex | OGL3 / EU 2011/833 |
| B | Guidance, persuasive | Quarterly curated verbatim quotes via human-merged PR | OGL3 / W3C Document License |
| C | Standards, proprietary | External index only (title + URI + one-sentence neutral description) | Third-party, fair-dealing |

## Schedule

GitHub Actions runs `build.py` monthly. Drift opens a PR. Merge to `main` tags `v<YYYY.MM.DD>`.

## Licences

- **Code** (`build.py`, `lib/`, `tests/`): MIT. See `LICENSE-CODE`.
- **Corpus**: layered. See `LICENSE-CORPUS`.
