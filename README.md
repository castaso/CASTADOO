# CASTADOO

CASTADOO is a rebranded distribution of [Odoo 17.0](https://github.com/odoo/odoo/tree/17.0),
maintained by CASTASOFT. It is the same ERP and business-app suite, with the user-visible
branding replaced: the web client and login page, notification e-mail footers, PDF report
metadata, the Windows installer, the progressive-web-app manifest and the offline page.

Upstream <https://castasoft.yukreasi.id>

## What this repository is

A **fork of Odoo 17.0**, not a set of patches on top of a published package. Two branches
matter, and they are not interchangeable:

| Branch | Contents | Rule |
|---|---|---|
| `17.0` | a byte-for-byte mirror of `odoo/odoo` 17.0 | **never edited** |
| `castadoo/17.0` | the default branch; the rebrand overlay | all work happens here |

`17.0` exists so that syncing an upstream point release is a fast-forward, and so that
"is this tree still pristine?" is a single commit comparison. The overlay is small on
purpose: a handful of in-place string edits, one new addon tree under `castadoo/`, and
the documentation in `docs/`. If you are contributing or deploying, branch from
`castadoo/17.0`.

The rebrand is implemented as addons wherever an addon can reach the surface, because an
addon does not create upstream conflict surface. Only the surfaces that an addon cannot
reach — the Windows installer, the PWA manifest controller, the database manager, the
release metadata — are edited in place.

## Getting started

Standard Odoo installation applies; the deployment notes in `docs/` add one requirement:
`<repo>/castadoo` must appear in `addons_path`, before the upstream addons, or the
branding addons are invisible and the rebrand silently does not apply.

Odoo 17.0 requires **Python 3.10** and a PostgreSQL server. Upstream's own installation,
developer and API documentation is the reference for everything except the branding
itself, and it is kept because it describes the software this fork actually is.

## Licensing

CASTADOO is distributed under the **GNU Lesser General Public License, version 3**, the
same licence as upstream Odoo, and that licence is unchanged by this fork. See `LICENSE`.

Copyright in the original work remains with Odoo S.A. and the many third-party
contributors; see `COPYRIGHT`. CASTASOFT's changes are additionally copyright CASTASOFT.
Renaming does not transfer copyright, and nothing in this repository should be read as
claiming it.

Because the licence is unchanged and the work is a modified version, the modified source
is published here in full, at the same paths as upstream wherever a file was edited.

## Security

Security issues in Odoo itself should go to upstream through the responsible-disclosure
process described in `SECURITY.md`, which is upstream's own file, kept verbatim: this fork
does not have the resources to triage the upstream codebase, and forwarding them there is
faster for everyone. Issues in the CASTADOO additions — the addons under `castadoo/`, the
installer edits, the deployment notes — should go to CASTASOFT.
