# Open Reason source matrix

Discovery is not ingestion. `enabled: true` requires license review.
**Open Reason does not use Reddit as a data source.**
Quora is not a primary source of truth.

| Source | Domain | Authority | License | Redistribution | Commercial | Attribution | Derivatives | Content types | Status | Enabled | Ingestion method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open Reason authors (`open-reason-authors`) | programming, mathematics, science, reasoning, education | high | CC-BY-4.0 | allowed | allowed | True | allowed | authored_in_repository | approved | yes | authored_in_repository |
| Open Reason generators (`open-reason-generators`) | programming, mathematics, science, reasoning | medium | CC-BY-4.0 | allowed | allowed | True | allowed | deterministic_generation | approved | yes | deterministic_generation |
| Reddit (`reddit`) | n/a | none | n/a | forbidden | forbidden | n/a | forbidden | n/a | prohibited | no | none |
| Quora (`quora`) | n/a | none | review_required | forbidden | forbidden | n/a | forbidden | n/a | prohibited | no | none |
| Khan Academy Computing (`khan_academy_computing`) | programming, computer_science | high | Terms of use / copyright; not assumed CC | review_required | review_required | True | review_required | structured_content, metadata | conditionally_approved | yes | structured_content, metadata |
| MIT OpenCourseWare (`mit_opencourseware`) | programming, mathematics, physics, engineering, computer_science | high | CC-BY-NC-SA-4.0 | restricted | no_if_nc | True | share_alike_if_sa | course_pages, metadata | conditionally_approved | yes | course_pages, metadata |
| Harvard CS50 (`harvard_cs50`) | programming, computer_science | high | Per-asset; lectures, notes, and problem sets may differ | review_required | review_required | True | review_required | metadata, concept_progression | conditionally_approved | yes | metadata, concept_progression |
| OpenStax (`openstax`) | computer_science, mathematics, physics, chemistry, biology, statistics, economics | high | CC-BY-4.0 | review_required | review_required | True | review_required | textbook, exercises, metadata | conditionally_approved | yes | textbook, exercises, metadata |
| MDN Web Docs (`mdn`) | web, javascript, html, css, accessibility, http | high | CC-BY-SA-2.5 | review_required | review_required | True | share_alike_likely | structured_docs | conditionally_approved | yes | structured_docs |
| The Odin Project (`the_odin_project`) | web, javascript, ruby, git, databases | medium | Curriculum and website code have different licenses | review_required | review_required | True | review_required | metadata, taxonomy | conditionally_approved | yes | metadata, taxonomy |
| Python official documentation (`python_docs`) | python, programming | high | PSF-2.0 | review_required | review_required | True | review_required | version_pinned_docs | conditionally_approved | yes | version_pinned_docs |
| Rust official documentation (`rust_docs`) | rust, programming | high | Apache-2.0 OR MIT | review_required | review_required | True | review_required | version_pinned_docs | conditionally_approved | yes | version_pinned_docs |
| Go official documentation (`go_docs`) | go, programming | high | BSD-3-Clause | review_required | review_required | True | review_required | version_pinned_docs | conditionally_approved | yes | version_pinned_docs |
| W3C / WHATWG specifications (`w3c_whatwg`) | web, html, http | high | Per-spec document license | review_required | review_required | True | review_required | specification_text | conditionally_approved | yes | specification_text |
| SQLite documentation (`sqlite_docs`) | sql, databases | high | blessing | review_required | review_required | True | review_required | version_pinned_docs | conditionally_approved | yes | version_pinned_docs |
| PostgreSQL documentation (`postgresql_docs`) | sql, databases | high | PostgreSQL | review_required | review_required | True | review_required | version_pinned_docs | conditionally_approved | yes | version_pinned_docs |
| Linux man-pages (`linux_man_pages`) | linux, operating_systems | high | Per-page; often GPL or BSD variants | review_required | review_required | True | review_required | man_pages | conditionally_approved | yes | man_pages |
| NASA educational resources (`nasa_education`) | astronomy, physics, earth_science | high | Often US government work / public domain, but not always | review_required | review_required | True | review_required | educational_pages, datasets | conditionally_approved | yes | educational_pages, datasets |
| NOAA educational resources (`noaa_education`) | earth_science, environmental_science | high | Often US government work; verify third-party material | review_required | review_required | True | review_required | educational_pages, datasets | conditionally_approved | yes | educational_pages, datasets |
| USGS educational resources (`usgs_education`) | earth_science | high | Often US government work; verify | review_required | review_required | True | review_required | educational_pages, datasets | conditionally_approved | yes | educational_pages, datasets |
| OpenAlex (`openalex`) | research, science | medium | CC0-1.0 | review_required | review_required | True | review_required | metadata, citation_graph | metadata_only | no | metadata, citation_graph |
| Stack Exchange network (`stack_exchange`) | programming, mathematics, science, systems | community_validated | CC-BY-SA-4.0 | review_required | allowed_with_sa | True | share_alike | data_dump, api | review_required | no | data_dump, api |
| Stack Overflow (`stackoverflow`) | programming | community_validated | CC-BY-SA-4.0 | review_required | allowed_with_sa | True | share_alike | data_dump, api | review_required | no | data_dump, api |
| Permissive Git repositories (`github_permissive`) | programming | medium | Per-repository SPDX allowlist | per_repo | per_repo | True | per_repo | commit_pinned_snapshot | review_required | no | commit_pinned_snapshot |
| OER Commons (`oer_commons`) | education | medium | Per-resource | review_required | review_required | True | review_required | metadata | conditionally_approved | yes | metadata |
| Wikibooks (`wikibooks`) | education | medium | CC-BY-SA-3.0 | review_required | allowed_with_sa | True | share_alike | wiki_export | conditionally_approved | yes | wiki_export |
| Wikipedia (`wikipedia`) | general | medium | CC-BY-SA-4.0 | review_required | allowed_with_sa | True | share_alike | n/a | review_required | no | none |

Educational value, technical value, verification potential, and freshness
are scored during discovery and are not a license grant.
