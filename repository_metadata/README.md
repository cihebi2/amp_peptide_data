# Repository snapshot metadata

This directory records transformations needed to publish the working dataset
as a portable GitHub repository without silently changing scientific content.

- `compressed_large_files.json`: lossless gzip replacements, original sizes,
  original SHA-256 digests, and compressed paths.
- `portable_symlink_conversion.json`: absolute local symlinks rewritten to
  repository-relative links, plus links removed because their targets are
  local-only source/cache material.
- `pruned_duplicate_and_source_surfaces.json`: duplicate intermediate finals
  and derived full-text source surfaces omitted from the public snapshot.
- `local_only_artifact_inventory.tsv.gz`: path/size/mtime/reason inventory for
  raw source binaries, caches, generated databases, and runtime streams kept
  outside Git.
- `local_only_artifact_inventory_summary.json`: bounded summary of that
  inventory.

No canonical final evidence row is rewritten by these repository packaging
steps. Large structured files are compressed byte-for-byte and carry the
digest of their uncompressed source.

