# Change Log for RegEx4Seq Project

Following the style in https://keepachangelog.com/en/1.0.0/

## [0.3.1] Bug fix

### Fixed

- A significant error in the `otherwise` method has been repaired.


## [0.3.0] Improved and unified the matches method, 2023-08-31

We have reached our first stable (or near-stable) point. The main missing
elements are docstrings, some readthedocs content and most importantly unit
tests - the existing tests have only very light coverage.

### Added

- The signature of `.matches`` has additional optional arguments. In particular
  the prefixes arguments gives a means for finding all possible matches of
  a match group.

- The signatures of `.findAllMatches` has been unified with `.matches`.

- Added type hinting throughout.

- CircleCI integration.

- Reduced the number of gaps in the documentation.

