Contributing to Odoo
====================

[Full contribution guidelines](https://github.com/odoo/odoo/wiki/Contributing)

TL;DR

* If you [make a pull request](https://github.com/odoo/odoo/wiki/Contributing#making-pull-requests),
  do not create an issue! Use the PR description for that
* Issues are handled with a much lower priority than pull requests
* Use this [template](https://github.com/odoo/odoo/wiki/Contributing#reporting-issues)
  when reporting issues. Please search for duplicates first!
* Pull requests must be made against the [correct version](https://github.com/odoo/odoo/wiki/Contributing#against-which-version-should-i-submit-a-patch)
* There are restrictions on the kind of [changes allowed in stable series](https://github.com/odoo/odoo/wiki/Contributing#what-does-stable-mean)

CASTADOO: how this fork differs
-------------------------------

The guidelines above describe the codebase and are worth reading before changing anything
under `addons/`. Three things are different here, and they take precedence.

**Branches.** `17.0` is a byte-for-byte mirror of upstream and is **never edited**; all work
happens on `castadoo/17.0`, the default branch. "Pristine" means `git rev-parse 17.0` equals
`git rev-parse upstream/17.0`.

**Syncing.** Upstream is synced at point releases only: fast-forward `17.0`, then
`git merge --no-ff 17.0` into `castadoo/17.0`. Never force-push either branch, so deployments
can pin a commit, and read overlay history with `git log --first-parent castadoo/17.0`.

**Conflicts.** Replaced binaries are covered by `merge=ours` rules in `.gitattributes`, which
need `git config merge.ours.driver true` once per clone or git silently falls back to a normal
merge. That driver suppresses the conflict; it does not license skipping the read. The three
replaced SVGs are deliberately excluded because they are text. Several identifiers in
`setup/win32/setup.nsi` must stay as upstream spells them and are marked `FROZEN` or `LEGACY`
at their site: a search-and-replace over that file breaks an upgrade path.

**Branding addons.** They live in `castadoo/`, split into `castadoo_branding` (depends on
`web` only) and one `castadoo_branding_<module>` overlay per surface. Two traps: an
`auto_install` overlay only fires when its target is *newly* entering installation, so an
overlay for an already-installed target needs an explicit `-i castadoo_branding_<new>` in
that release; and a view file not listed in the manifest's `data`, or a `static/src` file not
in an `assets` bundle, is inert — the module installs and the string gate passes while the
surface stays unbranded.

**Before pushing**, check that every manifest path exists, that every `inherit_id` /
`t-inherit` parent resolves and every `xpath` matches exactly one node (zero or many raises
at install), that Python compiles and XML parses, and that the POS receipt still reads
CASTADOO on a printed receipt — POS template inheritance fails *silently*, so a browser check
is not enough. Record the change in `docs/change_register.md`.

**Licensing.** The LGPL-3 is unchanged. New files carry a CASTADOO header stating LGPL-3 and
acknowledging derivation from Odoo 17.0; files edited in place keep their original copyright
header, and the licence text in `setup/win32/static/doc/License.rtf` stays verbatim.
Attribution is not a branding surface: the name `Odoo`, the copyright lines, the upstream
documentation links and upstream modules' `author` fields all stay.
